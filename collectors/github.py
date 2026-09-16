#!/usr/bin/env python3
"""PIOS GitHub 采集器 —— 把 GitHub 仓库的元数据同步进 project 实体。

与本地 projects.py 互补，不冗余：
- projects.py 采本地 ~/Projects 的 git 活动（提交数/最近改动）；
- github.py 采 GitHub 特有信息（公开/私有、语言、star、URL）+ 只在远程没 clone 的仓库（如 fork）。
- 通过 git remote URL 把本地目录与 GitHub 仓库对上（如本地 ai-fundamental-researcher = 远程 stock-pilot），
  对上就 enrich 同一个实体，避免重复。

纪律同 projects.py：不生成 commit 事件；只重写 GITHUB 块，保留手动内容。
用法：python3 collectors/github.py    需 gh 已登录。
"""
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT_PROJECTS = ROOT / "vault" / "projects"
PROJECTS_DIR = Path.home() / "Projects"
USER = "Hawisweary"
SKIP = {"pios-vault"}          # 私有数据仓库，不是"项目"
GH_START = "<!-- GITHUB:START (自动生成，勿手改此块) -->"
GH_END = "<!-- GITHUB:END -->"


def gh_repos():
    r = subprocess.run(
        ["gh", "repo", "list", USER, "--json",
         "name,visibility,primaryLanguage,stargazerCount,pushedAt,description,isFork,url",
         "--limit", "100"],
        capture_output=True, text=True)
    if r.returncode != 0:
        print("gh 出错（未登录？）:", r.stderr.strip())
        return []
    return json.loads(r.stdout or "[]")


def local_remote_map():
    """{github_repo_name_lower: local_dir_name} —— 通过各本地仓库的 origin 远程 URL 反查。"""
    m = {}
    if not PROJECTS_DIR.exists():
        return m
    for d in PROJECTS_DIR.iterdir():
        if not (d / ".git").exists():
            continue
        url = subprocess.run(["git", "-C", str(d), "remote", "get-url", "origin"],
                             capture_output=True, text=True).stdout.strip()
        mm = re.search(r"[:/]([\w.-]+?)(?:\.git)?$", url)
        if mm:
            m[mm.group(1).lower()] = d.name
    return m


def gh_block(repo):
    lang = (repo.get("primaryLanguage") or {}).get("name", "—")
    vis = repo["visibility"].lower()
    fork = " · fork" if repo.get("isFork") else ""
    return "\n".join([
        GH_START,
        f"- GitHub: **{vis}**{fork} · {lang} · ⭐{repo['stargazerCount']} · 最近 push {repo['pushedAt'][:10]}",
        f"- {repo['url']}",
        f"- 同步于 {datetime.now():%Y-%m-%d %H:%M}",
        GH_END,
    ])


def upsert(name, repo, category):
    VAULT_PROJECTS.mkdir(parents=True, exist_ok=True)
    f = VAULT_PROJECTS / f"{name}.md"
    block = gh_block(repo)
    if f.exists():
        t = f.read_text()
        if GH_START in t:
            t = re.sub(re.escape(GH_START) + ".*?" + re.escape(GH_END), lambda _: block, t, flags=re.S)
        elif "<!-- ACTIVITY:END -->" in t:                       # 插在活动块之后
            t = t.replace("<!-- ACTIVITY:END -->", "<!-- ACTIVITY:END -->\n\n" + block, 1)
        else:
            t = t.rstrip() + "\n\n" + block + "\n"
        f.write_text(t)
        return "updated"
    desc = repo.get("description") or "（GitHub 仓库）"
    f.write_text(f"""---
type: project
id: project:{name}
name: {name}
repo: github.com/{USER}/{repo['name']}
category: {category}
status: active
---

# {name}

{desc}

{block}

## 备注（手动）
""")
    return "created"


def main():
    m = local_remote_map()
    n = 0
    for repo in gh_repos():
        if repo["name"] in SKIP:
            continue
        local = m.get(repo["name"].lower())
        target = local or repo["name"]                          # 对上则 enrich 本地实体
        category = "reference" if repo.get("isFork") else "project"   # fork = 学习资源
        action = upsert(target, repo, category)
        tag = f"（本地 {local}）" if local else "（GitHub-only）"
        print(f"  {action:8} {repo['name']:22} → project:{target} {tag}")
        n += 1
    print(f"同步 {n} 个 GitHub 仓库")


if __name__ == "__main__":
    main()
