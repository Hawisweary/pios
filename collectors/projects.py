#!/usr/bin/env python3
"""PIOS 项目采集器 —— 把 ~/Projects 下的 git 仓库自动同步成 project 实体。

纪律（见对话中的设计决定）：
- 只自动采「描述 + 活动信号」，给 Athena 当上下文；
- **不**从 commits 生成事件（提交数是噪音，不是 depth-4 证据）；
- **不**自动编「功能清单」（易漂移/幻觉）；
- 真正的里程碑（"上线了 X 功能"）由你手动 `pios log project --depth 4`；
- 保留手动编辑：每次只重写 ACTIVITY 块，其余（描述、备注）原样保留。

用法：python3 collectors/projects.py
输出：vault/projects/<name>.md（私有仓库）
"""
import re
import subprocess
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

PROJECTS_DIR = Path.home() / "Projects"
ROOT = Path(__file__).resolve().parent.parent          # ~/Projects/pios
VAULT_PROJECTS = ROOT / "vault" / "projects"

TOOLING = {"pios", "hub"}   # 自建工具——单独归类，配合"≤15% 花在 PIOS 上"的元工作护栏
AUTO_START = "<!-- ACTIVITY:START (自动生成，勿手改此块) -->"
AUTO_END = "<!-- ACTIVITY:END -->"


def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return r.stdout.strip()


def readme_desc(repo):
    for name in ("README.md", "readme.md", "Readme.md"):
        f = repo / name
        if not f.exists():
            continue
        for para in f.read_text(errors="ignore").split("\n\n"):
            lines = []
            for l in para.splitlines():
                s = l.strip().lstrip("> ").strip()          # 去引用符
                if not s or s.startswith(("#", "!", "[!", "<", "|", "-", "```")):
                    continue                                 # 跳过标题/徽章/图片/表格/列表
                lines.append(s)
            text = " ".join(lines).strip()
            if len(text) > 20:
                return text[:280]
    return ""


def activity_block(repo):
    since = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    total = git(repo, "rev-list", "--count", "HEAD") or "0"
    d30 = git(repo, "rev-list", "--count", f"--since={since}", "HEAD") or "0"
    last = git(repo, "log", "-1", "--format=%cd", "--date=short")
    files = git(repo, "log", f"--since={since}", "--name-only", "--format=").splitlines()
    dirs = Counter(f.split("/")[0] for f in files if f.strip())
    top = ", ".join(d for d, _ in dirs.most_common(4))
    out = [AUTO_START,
           f"- 总提交 **{total}** · 近30天 **{d30}** · 最近提交 {last or '—'}"]
    if top:
        out.append(f"- 近30天改动集中在：{top}")
    out.append(f"- 同步于 {datetime.now():%Y-%m-%d %H:%M}")
    out.append(AUTO_END)
    return "\n".join(out)


def upsert(name, repo):
    VAULT_PROJECTS.mkdir(parents=True, exist_ok=True)
    f = VAULT_PROJECTS / f"{name}.md"
    block = activity_block(repo)
    if f.exists():
        t = f.read_text()
        if AUTO_START in t and AUTO_END in t:
            t = re.sub(re.escape(AUTO_START) + ".*?" + re.escape(AUTO_END),
                       lambda _: block, t, flags=re.S)
        else:
            t = t.rstrip() + "\n\n" + block + "\n"
        f.write_text(t)
        return "updated"
    category = "tooling" if name in TOOLING else "project"
    desc = readme_desc(repo) or "（补一句这个项目是做什么的）"
    f.write_text(f"""---
type: project
id: project:{name}
name: {name}
repo: ~/Projects/{name}
category: {category}
status: active
---

# {name}

{desc}

{block}

## 备注（手动：里程碑、想法、关联的技能/概念）
""")
    return "created"


def main():
    if not PROJECTS_DIR.exists():
        print("找不到 ~/Projects")
        return
    results = []
    for d in sorted(PROJECTS_DIR.iterdir()):
        if d.is_dir() and (d / ".git").exists():
            results.append((d.name, upsert(d.name, d)))
    for name, action in results:
        print(f"  {action:8} project:{name}")
    print(f"同步 {len(results)} 个项目 → vault/projects/")


if __name__ == "__main__":
    main()
