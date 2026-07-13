# PIOS — Personal Intelligence Operating System

> Athena 是它的默认 Mentor Agent。BCIC 定义"学什么"，PIOS 决定
> "今天学什么、为什么、学到什么程度、下一步是什么"。

治理与哲学见 [Constitution.md](Constitution.md) 和 [docs/PRINCIPLES.md](docs/PRINCIPLES.md)。

## 两种状态

```
Immutable（事实层，git 追踪）      events/*.jsonl · proposals/*.jsonl · vault/**/*.md
Derived（投影层，随时可焚毁重建）   pios.db · briefings/ · 一切分数与视图
```

## 目录结构

```
Constitution.md        宪法（11 条）
docs/PRINCIPLES.md     架构原则 · 四对象世界观 · 成功标准 · 死亡陷阱
schema.sql             derived index 的表结构
events/YYYY/MM.jsonl   事件流（append-only，唯一事实源之一）
proposals/YYYY/MM.jsonl  AI 提案与人的裁决（也是事实）
vault/                 知识库（Markdown + git = Knowledge Evolution）
  identity/            profile 与 role profiles
  curriculum/          BCIC 结构化课程 DAG
  concepts/ papers/ projects/ people/    图谱实体
  ideas/ decisions/ experiments/         研究与决策记录
  journal/ milestones/ templates/
agents/mentor/         Athena 的 briefing prompt
collectors/            L0 采集器（Phase 1）
engines/               L2 引擎（Phase 1+）
briefings/             每日输出（derived）
scripts/pios.py        CLI
```

## 快速开始

```bash
python3 scripts/pios.py init          # 建 derived index
python3 scripts/pios.py log lecture --entity concept:vector-space --depth 1
python3 scripts/pios.py events        # 最近 7 天
python3 scripts/pios.py rebuild       # 焚毁重建演习（Article 9 验收）
```

记录一个决策/想法/实验：复制 `vault/templates/` 对应模板到
`vault/decisions|ideas|experiments/`，填写后 `pios rebuild` 会自动入图谱。

## 路线图

- **Phase 0（现在）** 骨架 + 事件流 + 手动记录 + 每日 briefing。
  里程碑：**连续 14 天早上收到 briefing 并照做**。
- **Phase 1（第 1 学期）** collectors（GitHub/论文/课程）+ Skill Engine v1（证据深度×多样性）+ FSRS + proposal 审批回路 + 周报 + 月度抽测。
- **Phase 2（第 2 学期）** 夜间 Reflection Pass（reschedule/merge_idea/exploration 提案）+ Capability 聚合 + Twin gap 分析。
- **Phase 3（第 2 年起）** Time Machine 时间轴 + Calibration 曲线（Brier）+ Investment/Career 投影 + Dashboard（:8200/:3200 已在 dev hub 注册）。
