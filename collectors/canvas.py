#!/usr/bin/env python3
"""PIOS Canvas 采集器 —— 从 bCourses 拉作业元数据 + 我的成绩（不碰课程材料）。

只拉：作业名、截止日、满分、我的分数/状态。**绝不**拉 slide/阅读/文件内容
（守 ESPM/CS61A 的 AI 政策：不把课程材料给 AI）。数据留在本地私有 vault。
Token 从环境变量 CANVAS_TOKEN 读（放 .env.local，永不提交）。
**不**写入 depth 事件流（那是手动、带 depth 标签的能力证据）——这里只是成绩/截止日看板。

用法：source .env.local && python3 collectors/canvas.py
"""
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://bcourses.berkeley.edu/api/v1"
OUT = ROOT / "vault" / "canvas" / "assignments.md"
# Canvas 课程名关键词 → curriculum slug（只采这些学术课，跳过迎新/合规课）
MATCH = {"CS 61A": "cs61a", "ESPM 15": "espm-15", "GLOBAL 10B": "global-10b", "R4A": "colwrit-r4a"}


def api(path):
    tok = os.environ.get("CANVAS_TOKEN")
    if not tok:
        raise SystemExit("需要 CANVAS_TOKEN —— 先 `source .env.local`")
    r = subprocess.run(["curl", "-s", "-H", f"Authorization: Bearer {tok}", BASE + path],
                       capture_output=True, text=True, timeout=30)
    data = json.loads(r.stdout or "null")
    if isinstance(data, dict) and data.get("errors"):
        raise SystemExit(f"Canvas API 错误: {data['errors']}")
    return data


def match_course(c):
    text = (c.get("name", "") + " " + c.get("course_code", "")).upper()
    for kw, slug in MATCH.items():
        if kw.upper() in text:
            return slug
    return None


def grade(a):
    s = a.get("submission") or {}
    score, pts = s.get("score"), a.get("points_possible")
    if score is not None:
        return f"**{score}/{pts}**"
    if s.get("workflow_state") == "submitted":
        return "已交·未评"
    return "—"


def main():
    courses = api("/courses?enrollment_state=active&per_page=100")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    blocks = []
    for c in sorted(courses, key=lambda c: c.get("course_code", "")):
        slug = match_course(c)
        if not slug:
            continue
        assigns = api(f"/courses/{c['id']}/assignments?include[]=submission&per_page=100")
        rows = []
        for a in sorted(assigns, key=lambda a: a.get("due_at") or "9999"):
            due = (a.get("due_at") or "—")[:10]
            rows.append(f"| {a.get('name', '?')[:42]} | {due} | {a.get('points_possible', '?')} | {grade(a)} |")
        blocks.append(f"## {slug}（{c.get('course_code', '')}）\n\n"
                       f"| 作业 | 截止 | 满分 | 我的 |\n|---|---|---|---|\n" + "\n".join(rows))
    OUT.write_text("# Canvas 作业 + 成绩看板\n\n"
                   "> 自动从 bCourses 拉取（仅元数据 + 我的成绩，**不含课程材料**）。\n"
                   "> CS61A 不在此（用 cs61a.org/Gradescope/PrairieLearn）。Blockchain Decal 无 bCourses 页。\n\n"
                   + "\n\n".join(blocks) + "\n")
    print(f"已写 {OUT}（{len(blocks)} 门课）")


if __name__ == "__main__":
    main()
