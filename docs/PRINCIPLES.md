# PIOS Architecture Principles

这份文档是设计哲学层。它约束"该不该做"，[Constitution.md](../Constitution.md) 约束"绝不能做"。

## 四个核心对象（世界观，不是 Schema）

一切功能必须能表达为以下四者的投影，否则拒绝（Constitution Article 8）：

| 对象 | 含义 | 物理对应 |
|---|---|---|
| **Memory** | 发生过什么 | 事件流（vault/events/*.jsonl）、journal、FSRS 记忆状态 |
| **Knowledge** | 我知道什么 | Vault Markdown + 图谱（entities/edges） |
| **Decision** | 我选择了什么 | decision 实体 + proposals 裁决记录 |
| **Action** | 我做了什么 | 事件流中的行为事件（commit / exercise / experiment...） |

投影示例：Skill = Memory × Action；Capability = Knowledge × Action；Career = Decision × Action；Research = Knowledge × Decision × Action。

## 两种状态（No Hidden State Principle）

```
Immutable（事实层，私有仓库 vault/）  vault/events/*.jsonl · vault/proposals/*.jsonl · vault/briefings/ · vault/ 的 git 历史
Derived（投影层）                     pios.db 全部内容 · dashboard · 一切分数
```

判据：记录"发生过什么"的归事实层；回答"现在意味着什么"的归投影层。

Derived state **可以物化，但永远不是权威**。验收标准：

```
rm pios.db && pios rebuild   # 结果必须与删除前完全一致
```

每年执行一次全量重建演习（长期可迁移验收）。

## 分层架构（PIOS v3）

```
L4  交互      Daily Briefing · Time Machine · Dashboard · Proposal 审批
L3.5 推理回路  夜间 Reflection Pass → Proposals（可审计提案）
L3  Agent     Mentor(Athena) · Research · Review
L2  引擎      Skill+Capability(证据深度×多样性+FSRS) · Twin · Learning · Calibration
L1  存储      事件流(JSONL) · 图谱(entities/edges) · Vault(Markdown) · pios.db(derived index)
L0  采集      GitHub · 课程 · 论文 · 券商 · 日记 · Quiz
```

## 证据深度阶梯（Epistemic Engine）

```
深度 1  听过（lecture / 泛读）
深度 2  读懂（精读 + summary）
深度 3  用过（习题 / 调 API）
深度 4  造过（从零实现 / 复现）
深度 5  教过（blog / 讲课 / 答疑）

confidence = f(最高深度, 深度种类数, 时效)
```

Knowledge confidence、Skill level、Capability 共用这一个模型，只是聚合粒度不同。

## 提案纪律

- AI 的一切主动性以 Proposal 形式落库，等待人批准（Constitution Article 3）。
- `exploration`（好奇心）类提案永远不进课表、不计完成率，在 briefing 中单列"发现"区。
- Idea 永不自动合并，只生成 `merge_idea` 提案。

## 四年成功标准（每月由系统自动计算）

| 指标 | 衡量标准 | 代理指标 |
|---|---|---|
| 完整性 | ≥95% 的学习/项目/研究/投资/重要决策可追溯到原始事件 | 每周 Mentor 漏报问询 |
| 可解释性 | 任何分数/建议可追溯到事件、证据和推理链 | 架构保证 + 钻取视图 |
| 持续使用 | 连续四年使用，数据以自动采集为主 | `source=manual` 事件占比 |
| 成长价值 | 持续发现缺口、形成研究成果、改进决策 | proposal 采纳率 + 被采纳提案的后续证据 |
| 长期可迁移 | 10 年后 Markdown + 事件流 + 图谱仍完整可用 | 年度 `rebuild --from-scratch` 演习 |

## 死亡陷阱清单（按杀伤力排序）

1. **元工作陷阱**：建 PIOS 的时间挤掉学习时间。硬规则：每周开发投入 ≤15%，PIOS 自己追踪并报警。
2. **手动录入死亡螺旋**：默认自动采集；手动输入只保留日记和 decision thesis。
3. **数字自欺**：无抽测校准的分数是通胀货币。每月对涨最快的 2-3 个技能抽测。
4. **过度工程**：SQLite + Markdown + git 能撑四年。护城河是数据，不是技术栈。
5. **好奇心被调度器接管**：exploration 变成待办事项之日，即 Curiosity Engine 死亡之日。
