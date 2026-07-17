# 02 · Architecture

## 三条设计公理

1. **一切皆事件（Event）**——你做的每件事都是一条不可变记录。唯一事实源。
2. **一切皆图谱节点（Entity）**——知识点、论文、项目、股票、技能、目标都是实体，之间是边。
3. **其余一切皆投影（Projection）**——技能分数、周报、Twin 匹配、Daily Briefing，
   全部可从 Event + Vault 重算，所以永远不会"错"，只会"过时后被重算刷新"。

这是它是 OS 而非 App 的原因：App 存界面状态，OS 存不可变底层数据 + 可重算的上层视图。

## 分层

```
L4  交互      Daily Briefing · Time Machine · Dashboard · Proposal 审批
L3.5 推理回路  夜间 Reflection Pass → Proposals（可审计提案）
L3  Agent     Mentor(Athena) · Research · Review
L2  引擎      Skill+Capability · Twin · Learning(FSRS) · Calibration
L1  存储      事件流(JSONL) · 图谱(entities/edges) · Vault(Markdown) · pios.db(derived)
L0  采集      GitHub · 课程 · 论文 · 券商 · 日记 · Quiz
```

## 两种状态（No Hidden State）

```
Immutable（事实层，git 追踪）   events/*.jsonl · proposals/*.jsonl · vault/**/*.md
Derived（投影层，可焚毁重建）   pios.db · briefings/ · 一切分数与视图
```

判据：**记录"发生过什么"的归事实层；回答"现在意味着什么"的归投影层。**
Derived state 可以物化/缓存，但永远不是权威。验收测试（Constitution Article 9）：

```
rm pios.db && pios rebuild   # 结果必须与删除前逐字节一致
```

## 四个核心对象（世界观，不进 schema）

Memory / Knowledge / Decision / Action 是判断"该不该做某功能"的滤镜（凡不能表达为这四者
投影的功能，拒绝），**只活在文档里，不落成物理表**——抽象层级越高表达力越强、可查询性越差，
具体类型放 schema，统一世界观放文档。详见 [PRINCIPLES](../PRINCIPLES.md)。

## 技术选型（为"一个人维护四年"优化）

SQLite + Markdown + git 仓库 + Claude Agent SDK。零运维、可 grep、可 diff、
几十年后仍可打开。不用 Neo4j / Postgres / K8s / 云数据库 / 自训模型——图谱规模（几千节点）
用不上图数据库，护城河是数据不是技术栈。理由展开见 [08-roadmap](08-roadmap.md) 死亡陷阱。
