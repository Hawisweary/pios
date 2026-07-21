# PIOS — Personal Intelligence Operating System

> Athena 是它的默认 Mentor Agent。BCIC 定义"学什么"，PIOS 决定
> "今天学什么、为什么、学到什么程度、下一步是什么"。

## 文档体系（三层）

```
Constitution.md      Why & 不可违背   —— 最高法，极少改
docs/DESIGN/         What（系统全景）  —— 8 章，一小时读完
docs/PRINCIPLES.md   设计哲学速查
docs/rfc/            How（每个决策）   —— 一次一篇，按需生长
```

新读者阅读顺序：本 README → [Constitution](Constitution.md) →
[docs/DESIGN/](docs/DESIGN/README.md) → 代码。

## 两个仓库：公开的系统 + 私有的数据

PIOS 拆成两个 git 仓库，遵守 Constitution Article 5（个人知识属于用户）：

```
pios（公开）        这套软件——代码/文档/模板。别人 clone 即可搭自己的 PIOS
└── vault/（私有）  嵌套的独立私有仓库 pios-vault：Harry 四年的全部个人数据
```

公开仓库 `.gitignore` 掉 `vault/`，所以个人数据永远不进公开历史。

## 两种状态

```
Immutable（事实层，在私有仓库 vault/ 里，git 追踪）
    vault/events/*.jsonl · vault/proposals/*.jsonl · vault/briefings/ · vault/**/*.md
Derived（投影层，随时可焚毁重建）
    pios.db · 一切分数与视图
```

## 目录结构

```
【公开仓库 pios】
Constitution.md        宪法（13 条）
README.md              本文件
docs/PRINCIPLES.md     架构原则 · 四对象世界观 · 成功标准 · 死亡陷阱
docs/DESIGN/           系统设计（8 章）· docs/rfc/  设计决策
schema.sql             derived index 的表结构
templates/             decision / idea / experiment 模板（系统）
agents/mentor/         Athena 的 briefing prompt
collectors/            L0 采集器（Phase 1）
engines/               L2 引擎（Phase 1+）
scripts/pios.py        CLI

【私有仓库 vault/（pios-vault）】
vault/events/YYYY/MM.jsonl     事件流（append-only，唯一事实源之一）
vault/proposals/YYYY/MM.jsonl  AI 提案与人的裁决（也是事实）
vault/briefings/               每日 briefing（历史记录）
vault/identity/                profile 与 role profiles
vault/curriculum/              BCIC 结构化课程 DAG + 学位要求
vault/concepts/ papers/ projects/ people/   图谱实体
vault/ideas/ decisions/ experiments/        研究与决策记录
vault/journal/ milestones/
```

## 快速开始

```bash
python3 scripts/pios.py init          # 建 derived index
python3 scripts/pios.py log lecture --entity concept:vector-space --depth 1
python3 scripts/pios.py events        # 最近 7 天
python3 scripts/pios.py rebuild       # 焚毁重建演习（Article 9 验收）
```

记录一个决策/想法/实验：复制 `templates/` 对应模板到
`vault/decisions|ideas|experiments/`，填写后 `pios rebuild` 会自动入图谱。

## 路线图

- **Phase 0（现在）** 骨架 + 事件流 + 手动记录 + 每日 briefing。
  里程碑：**连续 14 天早上收到 briefing 并照做**。
- **Phase 1（第 1 学期）** collectors（GitHub/论文/课程）+ Skill Engine v1（证据深度×多样性）+ FSRS + proposal 审批回路 + 周报 + 月度抽测。
- **Phase 2（第 2 学期）** 夜间 Reflection Pass（reschedule/merge_idea/exploration 提案）+ Capability 聚合 + Twin gap 分析。
- **Phase 3（第 2 年起）** Time Machine 时间轴 + Calibration 曲线（Brier）+ Investment/Career 投影 + Dashboard（:8200/:3200 已在 dev hub 注册）。
