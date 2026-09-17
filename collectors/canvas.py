#!/usr/bin/env python3
"""PIOS Canvas 采集器 —— bCourses 作业/成绩/反馈/rubric（不碰课程材料）。

只拉：作业名·截止日·满分·我的分数·老师反馈评语·rubric 得分。**绝不**拉 slide/阅读/文件/页面内容
（守 ESPM/CS61A AI 政策）。数据留在本地私有 vault。Token 从 CANVAS_TOKEN（.env.local，永不提交）。
**不**写入 depth 事件流——这里只是成绩/截止日/反馈看板。running grade 自算"已评部分"（不用 Canvas
早期把未评按 0 计的误导数）。

用法：source .env.local && python3 collectors/canvas.py
"""
import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://bcourses.berkeley.edu/api/v1"
OUT = ROOT / "vault" / "canvas" / "assignments.md"
MATCH = {"CS 61A": "cs61a", "ESPM 15": "espm-15", "GLOBAL 10B": "global-10b", "R4A": "colwrit-r4a"}


def api(path):
    tok = os.environ.get("CANVAS_TOKEN")
    if not tok:
        raise SystemExit("需要 CANVAS_TOKEN —— 先 `source .env.local`")
    r = subprocess.run(["curl", "-s", "-H", f"Authorization: Bearer {tok}", BASE + path],
                       capture_output=True, text=True, timeout=45)
    data = json.loads(r.stdout or "null")
    if isinstance(data, dict) and data.get("errors"):
        raise SystemExit(f"Canvas API 错误（token 可能已撤，更新 .env.local）: {data['errors']}")
    return data


def match_course(c):
    text = (c.get("name", "") + " " + c.get("course_code", "")).upper()
    return next((slug for kw, slug in MATCH.items() if kw.upper() in text), None)


def rubric_lines(sub, assign):
    ra = sub.get("rubric_assessment") or {}
    if not ra:
        return []
    desc = {r["id"]: r.get("description", r["id"]) for r in (assign.get("rubric") or [])}
    out = []
    for cid, v in ra.items():
        pts = v.get("points")
        cm = (v.get("comments") or "").strip()
        line = f"    · {desc.get(cid, cid)[:30]}: {pts}分"
        if cm:
            line += f" — {cm[:60]}"
        out.append(line)
    return out


def main():
    courses = api("/courses?enrollment_state=active&per_page=100")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    blocks = []
    for c in sorted(courses, key=lambda c: c.get("course_code", "")):
        slug = match_course(c)
        if not slug:
            continue
        subs = api(f"/courses/{c['id']}/students/submissions?student_ids[]=self"
                   "&include[]=submission_comments&include[]=rubric_assessment&include[]=assignment&per_page=100")
        rows, feedback, got, total = [], [], 0.0, 0.0
        for s in sorted(subs, key=lambda s: (s.get("assignment") or {}).get("due_at") or "9999"):
            a = s.get("assignment") or {}
            due = (a.get("due_at") or "—")[:10]
            score, pts = s.get("score"), a.get("points_possible")
            if score is not None:
                flag = " ⚠" if (score == 0 and pts and s.get("workflow_state") == "graded") else ""
                grade = f"**{score}/{pts}**{flag}"
                if pts:
                    got += score
                    total += pts
            elif s.get("workflow_state") == "submitted":
                grade = "已交·未评"
            else:
                grade = "—"
            rows.append(f"| {a.get('name', '?')[:40]} | {due} | {pts} | {grade} |")
            cmts = [x.get("comment", "").strip() for x in (s.get("submission_comments") or []) if x.get("comment")]
            rlines = rubric_lines(s, a)
            if cmts or rlines:
                feedback.append(f"**{a.get('name', '?')}**（{score}/{pts}）")
                feedback += [f"    评语: {cm[:100]}" for cm in cmts]
                feedback += rlines
        graded = f"已评部分 **{got:.0f}/{total:.0f} = {got / total * 100:.0f}%**" if total else "暂无已评作业"
        block = f"## {slug}（{c.get('course_code', '')}）\n\n{graded}\n\n" \
                f"| 作业 | 截止 | 满分 | 我的 |\n|---|---|---|---|\n" + "\n".join(rows)
        if feedback:
            block += "\n\n**反馈 / rubric**\n\n" + "\n".join(feedback)
        blocks.append(block)
    OUT.write_text("# Canvas 作业 · 成绩 · 反馈看板\n\n"
                   "> 自动从 bCourses 拉（元数据 + 我的成绩/反馈，**不含课程材料**）。\n"
                   "> running grade 为自算的\"已评部分\"（Canvas 早期把未评按 0 计，不用它那个数）。\n"
                   "> CS61A 不在此（外部工具）；Blockchain Decal 无 bCourses 页。\n\n"
                   + "\n\n".join(blocks) + "\n")
    print(f"已写 {OUT}（{len(blocks)} 门课）")


if __name__ == "__main__":
    main()
