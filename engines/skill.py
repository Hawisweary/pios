"""PIOS Skill Engine v1 — RFC-0001.

概念强度 = 事件的（深度加权 × 外部验证加成 × 时间衰减）之和。纯投影：
不存任何分数，每次现算（Article 9）；每分可钻到证据（Article 7，见 why()）；
只读事实（Article 3）；确定性、stdlib-only、零 LLM。v1 只算概念（capability 聚合=Phase 2）。
"""
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone

DEPTH_WEIGHT = {1: 0.1, 2: 0.3, 3: 0.6, 4: 1.0, 5: 1.3}
VERIFIED_KINDS = {"quiz", "exam"}       # 外部验证 → 加成
VERIFY_BONUS = 1.2
HALF_LIFE_DAYS = 180


def _days_ago(ts):
    try:
        t = datetime.fromisoformat(ts)
    except ValueError:
        return 0.0
    if t.tzinfo is None:
        t = t.replace(tzinfo=timezone.utc)
    d = (datetime.now(timezone.utc) - t.astimezone(timezone.utc)).total_seconds() / 86400
    return max(0.0, d)


def _contrib(kind, depth, ts):
    if not depth:
        return 0.0
    w = DEPTH_WEIGHT.get(depth, 0.0)
    if kind in VERIFIED_KINDS:
        w *= VERIFY_BONUS
    return w * (0.5 ** (_days_ago(ts) / HALF_LIFE_DAYS))


def compute(con):
    """Return a list of per-concept dicts, sorted by current strength desc."""
    ev = defaultdict(list)           # concept -> [(ts, kind, depth)]
    dom = defaultdict(Counter)       # concept -> Counter(course)
    for ts, kind, depth, eids in con.execute(
            "SELECT ts, kind, depth, entity_ids FROM events WHERE depth IS NOT NULL"):
        ids = json.loads(eids)
        concepts = [e for e in ids if e.startswith("concept:")]
        courses = [e for e in ids if e.startswith("course:")]
        for c in concepts:
            ev[c].append((ts, kind, depth))
            for co in courses:
                dom[c][co] += 1

    names = dict(con.execute("SELECT id, name FROM entities WHERE type='concept'"))
    rows = []
    for cid, evs in ev.items():
        depths = {d for _, _, d in evs}
        kinds = {k for _, k, _ in evs}
        n = len(evs)
        conf = min(1.0, n / 5 * 0.5 + len(depths) / 3 * 0.3 + len(kinds) / 3 * 0.2)
        peak = max(depths)
        # 最近一次外部验证（quiz/exam）的深度 → 与峰值对比判断状态
        checks = sorted((t, d) for t, k, d in evs if k in VERIFIED_KINDS)
        if not checks:
            status = "unverified"          # 从没考过 → 仅自报
        elif checks[-1][1] >= peak:
            status = "verified"            # 最近一次验证达到峰值 → 可信
        else:
            status = "faded"               # 校准揭示当前 < 峰值 → 褪色
        rows.append({
            "id": cid,
            "slug": cid.split(":", 1)[1],
            "name": names.get(cid, cid.split(":", 1)[1]),
            "strength": round(sum(_contrib(k, d, t) for t, k, d in evs), 2),
            "max_depth": peak,
            "verified_depth": checks[-1][1] if checks else None,   # 最近验证到的深度
            "confidence": round(conf, 2),
            "n": n,
            "last": max(t for t, _, _ in evs)[:10],
            "domain": dom[cid].most_common(1)[0][0].split(":", 1)[1] if dom[cid] else "其他",
            "status": status,
        })
    rows.sort(key=lambda r: -r["strength"])
    return rows


def calibrate_candidates(con, min_depth=2):
    """待校准：从未被外部验证（status=unverified）的概念，按强度降序（通胀风险最高在前）。"""
    return [r for r in compute(con) if r["status"] == "unverified" and r["max_depth"] >= min_depth]


def why(con, concept_id):
    """Article 7 drill-down: every depth-bearing event tagging concept_id, with its contribution."""
    if not concept_id.startswith("concept:"):
        concept_id = "concept:" + concept_id
    out = []
    for ts, kind, depth, eids, payload in con.execute(
            "SELECT ts, kind, depth, entity_ids, payload FROM events ORDER BY ts"):
        if depth and concept_id in json.loads(eids):
            note = json.loads(payload).get("note", "")
            out.append({"ts": ts[:10], "kind": kind, "depth": depth,
                        "contrib": round(_contrib(kind, depth, ts), 3), "note": note})
    return out
