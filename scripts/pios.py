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


def cmd_log(args):
    ev = {
        "id": str(uuid.uuid4()),
        "ts": args.ts or now_iso(),
        "kind": args.kind,
        "source": args.source,
        "entity_ids": args.entity or [],
        "depth": args.depth,
        "payload": json.loads(args.payload),
    }
    with event_shard(ev["ts"]).open("a") as f:
        f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    con = connect()
    init_db(con)
    insert_event(con, ev)
    con.commit()
    print(f"logged {ev['kind']} {ev['id'][:8]} @ {ev['ts']}")


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

    p = sub.add_parser("events")
    p.add_argument("--days", type=int, default=7)

    sub.add_parser("rebuild")

    args = ap.parse_args()
    if args.cmd == "init":
        init_db(connect())
        print(f"initialized {DB}")
    elif args.cmd == "log":
        cmd_log(args)
    elif args.cmd == "events":
        cmd_events(args)
    elif args.cmd == "rebuild":
        cmd_rebuild(args)


if __name__ == "__main__":
    sys.exit(main())
