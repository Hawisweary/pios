#!/usr/bin/env python3
"""PIOS CLI — Phase 0.

Facts live in git-tracked text (events/*.jsonl, proposals/*.jsonl, vault/*.md).
pios.db is a derived index and can always be rebuilt (Constitution Article 9).

Usage:
  pios.py init                      create pios.db from schema.sql
  pios.py log KIND [options]        append an event (JSONL + db)
  pios.py events [--days N]         list recent events
  pios.py rebuild                   drop db, rebuild from JSONL + vault
"""
import argparse
import json
import re
import sqlite3
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "pios.db"


def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def connect():
    con = sqlite3.connect(DB)
    con.execute("PRAGMA journal_mode=WAL")
    return con


def init_db(con):
    con.executescript((ROOT / "schema.sql").read_text())
    con.commit()


def event_shard(ts: str) -> Path:
    d = datetime.fromisoformat(ts)
    p = ROOT / "events" / f"{d.year}" / f"{d.month:02d}.jsonl"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def insert_event(con, ev):
    con.execute(
        "INSERT OR REPLACE INTO events (id, ts, kind, source, entity_ids, depth, payload)"
        " VALUES (?,?,?,?,?,?,?)",
        (ev["id"], ev["ts"], ev["kind"], ev["source"],
         json.dumps(ev.get("entity_ids", []), ensure_ascii=False),
         ev.get("depth"),
         json.dumps(ev.get("payload", {}), ensure_ascii=False)),
    )


def append_event(ev):
    with event_shard(ev["ts"]).open("a") as f:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    con = connect()
    init_db(con)
    insert_event(con, ev)
    con.commit()
    print(f"logged {ev['kind']} {ev['id'][:8]} @ {ev['ts']}")


def cmd_log(args):
    append_event({
        "id": str(uuid.uuid4()),
        "ts": args.ts or now_iso(),
        "kind": args.kind,
        "source": args.source,
        "entity_ids": args.entity or [],
        "depth": args.depth,
        "payload": json.loads(args.payload),
    })


SAY_KINDS = "lecture|exercise|paper_read|project|teaching|quiz|journal|milestone"

SAY_PROMPT = """你是 PIOS 的学习事件解析器。把一句自然语言的学习记录解析成 JSON。
只输出一个 JSON 对象，不要输出任何其他文字、解释或 markdown 代码块。

字段：
- kind: {kinds} 之一（看课/泛读=lecture, 做题/lab=exercise, 精读+笔记=paper_read,
  写完项目=project, 教别人/写blog=teaching, 测验=quiz, 感想/日记=journal）
- entity_ids: 字符串数组，这件事关于哪些知识点/课程/项目。
  优先从下面的已有实体中精确选取；没有匹配的就新建，格式 "concept:english-kebab-slug"
- depth: 整数 1-5 或 null。1=听过/看过 2=读懂并总结 3=动手用过/做题 4=从零实现 5=教过别人。
  原文没有依据就填 null，不要猜高。
- date: 原文提到非今天的日期（如"昨天"、"周一"）则输出 "YYYY-MM-DD"，否则 null。今天是 {today}。
- note: 一句话保留原文关键信息。

已有实体：
{known}

记录原文：{text}"""


def cmd_say(args):
    import subprocess

    con = connect()
    init_db(con)
    known = [f"{r[0]} ({r[1]})" for r in con.execute("SELECT id, name FROM entities")]
    prompt = SAY_PROMPT.format(
        kinds=SAY_KINDS,
        today=datetime.now().strftime("%Y-%m-%d %A"),
        known="\n".join(known) or "(暂无)",
        text=args.text,
    )
    r = subprocess.run(
        ["claude", "-p", prompt, "--model", args.model],
        capture_output=True, text=True, timeout=180,
    )
    raw = r.stdout.strip()
    if raw.startswith("```"):
        raw = re.sub(r"\A```[a-z]*\n|\n```\Z", "", raw)
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        print(f"解析失败，模型输出：\n{raw or r.stderr}", file=sys.stderr)
        return 1

    ts = now_iso()
    if parsed.get("date"):
        local_tz = datetime.now().astimezone().tzinfo
        ts = datetime.fromisoformat(parsed["date"] + "T12:00:00").replace(tzinfo=local_tz).isoformat(timespec="seconds")
    ev = {
        "id": str(uuid.uuid4()),
        "ts": ts,
        "kind": parsed.get("kind", "journal"),
        "source": "say",
        "entity_ids": parsed.get("entity_ids", []),
        "depth": parsed.get("depth"),
        "payload": {"note": parsed.get("note", ""), "raw": args.text},
    }

    depth = f"depth {ev['depth']}" if ev["depth"] else "depth ?"
    print(f"\n  {ev['ts']}")
    print(f"  {ev['kind']}  [{depth}]  {', '.join(ev['entity_ids']) or '(无实体)'}")
    print(f"  {ev['payload']['note']}\n")

    if args.dry_run:
        print("(dry-run，未写入)")
        return
    if not args.yes:
        ans = input("写入事件流? [y/N] ").strip().lower()
        if ans not in ("y", "yes"):
            print("已取消")
            return
    append_event(ev)


def cmd_events(args):
    con = connect()
    init_db(con)
    since = (datetime.now(timezone.utc) - timedelta(days=args.days)).isoformat()
    rows = con.execute(
        "SELECT ts, kind, source, entity_ids, depth FROM events WHERE ts >= ? ORDER BY ts",
        (since,),
    ).fetchall()
    for ts, kind, source, ents, depth in rows:
        d = f" d{depth}" if depth else ""
        print(f"{ts}  {kind:<16} [{source}]{d}  {ents}")
    print(f"-- {len(rows)} events in last {args.days} days")


FRONTMATTER = re.compile(r"\A---\n(.*?)\n---", re.DOTALL)

# frontmatter keys that map to graph edges, and their relation names
EDGE_KEYS = {
    "prerequisites": "prerequisite_of",   # reversed: listed item -> this entity
    "sparked_by": "sparked_by",
    "spawned": "spawned",
    "superseded_by": "superseded_by",
    "alternative_to": "alternative_to",
    "evidence": "informed_decision",
    "idea": "motivated_by",
}


def parse_frontmatter(text):
    """Minimal YAML-ish frontmatter parser (flat keys + inline lists)."""
    m = FRONTMATTER.match(text)
    if not m:
        return {}
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.startswith((" ", "-", "#")):
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if " #" in v and not v.startswith("["):   # strip inline comment on scalar
            v = v.split(" #", 1)[0].strip()
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip() for x in v[1:-1].split(",") if x.strip()]
        meta[k.strip()] = v
    return meta


def cmd_rebuild(args):
    if DB.exists():
        DB.unlink()
    con = connect()
    init_db(con)

    n_ev = 0
    for shard in sorted((ROOT / "events").rglob("*.jsonl")):
        for line in shard.read_text().splitlines():
            if line.strip():
                insert_event(con, json.loads(line))
                n_ev += 1

    n_pr = 0
    for shard in sorted((ROOT / "proposals").rglob("*.jsonl")):
        for line in shard.read_text().splitlines():
            if not line.strip():
                continue
            p = json.loads(line)
            con.execute(
                "INSERT OR REPLACE INTO proposals VALUES (?,?,?,?,?,?,?)",
                (p["id"], p["ts"], p["kind"], p["rationale"],
                 json.dumps(p.get("diff", {}), ensure_ascii=False),
                 p.get("status", "pending"), p.get("decided_ts")),
            )
            n_pr += 1

    n_ent, n_edge = 0, 0
    for md in sorted((ROOT / "vault").rglob("*.md")):
        if md.parent.name == "templates":
            continue
        meta = parse_frontmatter(md.read_text())
        etype = meta.get("type")
        if not etype:
            continue
        eid = meta.get("id") or f"{etype}:{md.stem}"
        con.execute(
            "INSERT OR REPLACE INTO entities VALUES (?,?,?,?,?)",
            (eid, etype, meta.get("name", md.stem),
             str(md.relative_to(ROOT)), json.dumps(meta, ensure_ascii=False)),
        )
        n_ent += 1
        for key, rel in EDGE_KEYS.items():
            vals = meta.get(key)
            if isinstance(vals, str):
                vals = [vals]
            for dst in vals or []:
                src, d = (dst, eid) if key == "prerequisites" else (eid, dst)
                con.execute("INSERT OR REPLACE INTO edges VALUES (?,?,?)", (src, d, rel))
                n_edge += 1

    con.commit()
    print(f"rebuilt: {n_ev} events, {n_pr} proposals, {n_ent} entities, {n_edge} edges")


def main():
    ap = argparse.ArgumentParser(prog="pios")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("init")

    p = sub.add_parser("log")
    p.add_argument("kind")
    p.add_argument("--source", default="manual")
    p.add_argument("--entity", action="append", metavar="ENTITY_ID")
    p.add_argument("--depth", type=int, choices=range(1, 6))
    p.add_argument("--payload", default="{}")
    p.add_argument("--ts")

    p = sub.add_parser("say", help="自然语言记录事件：pios say '看完了CS61A第一讲'")
    p.add_argument("text")
    p.add_argument("--model", default="haiku")
    p.add_argument("--yes", action="store_true", help="跳过确认直接写入")
    p.add_argument("--dry-run", action="store_true", help="只解析不写入")

    p = sub.add_parser("events")
    p.add_argument("--days", type=int, default=7)

    sub.add_parser("rebuild")

    args = ap.parse_args()
    if args.cmd == "init":
        init_db(connect())
        print(f"initialized {DB}")
    elif args.cmd == "log":
        cmd_log(args)
    elif args.cmd == "say":
        return cmd_say(args)
    elif args.cmd == "events":
        cmd_events(args)
    elif args.cmd == "rebuild":
        cmd_rebuild(args)


if __name__ == "__main__":
    sys.exit(main())
