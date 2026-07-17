# 04 · Knowledge Graph（Knowledge 对象）

## 一张图，五个视图

Knowledge / Paper / People / Project / Decision 五种"图"不是五个存储，而是同一张图
（`entities` + `edges`）按 `type` 过滤出的五个视图。五个存储会带来同步不一致，一张图永远一致。

实体类型：concept / paper / project / person / idea / decision / experiment / milestone
（+ 投影用的 skill / course / role_profile）。
边：prerequisite_of / part_of / cites / applies / implements / motivated_by /
authored_by / influenced_by / informed_decision / superseded_by / alternative_to /
sparked_by / spawned。

## 知识演化（Knowledge Evolution）

知识不是静态图，是会成长的东西。"我对 MoE 的理解两年里怎么变的"这个问题，90% 由现有架构免费回答：

- Vault 在 git 里 → `git log vault/concepts/moe.md` 就是完整版本史；
- `first_seen` / `last_used` 不是字段，是对事件流的查询；
- Time Machine → 回放到任意时点的文档版本 + 当时证据集。

新增仅两样小东西：边 `superseded_by` / `alternative_to`（MoE→Sparse Routing 场景）；
事件 `belief_revision`（认知发生实质**修正**时显式标记，普通补充靠 git 自动记录）。

## 证据深度阶梯（Epistemic Engine）

每个概念/技能的 confidence 由证据的**深度 × 多样性**决定，不是数量：

```
深度 1  听过（lecture / 泛读）
深度 2  读懂（精读 + summary）
深度 3  用过（习题 / 调 API）
深度 4  造过（从零实现 / 复现）
深度 5  教过（blog / 讲课 / 答疑）

confidence = f(最高深度, 深度种类数, 时效)
```

Knowledge confidence、Skill level、Capability **共用这一个模型、同一张证据事件表**，
只是聚合粒度不同。Mentor 因此能建议"你的 Transformer 停在深度 2，下一步不是学新东西，是从零实现一次"。

## 学习引擎（Learning Engine）

不是简单 Scheduler，而是"课程 DAG + 记忆模型"的合流：

- **课程 DAG**：BCIC 每门课用 YAML frontmatter 声明 `prerequisites` 和 `skills_trained`，
  拓扑排序 + Twin gap 优先级 = 今天该学的新内容。难点在数据结构化，不在调度算法。
- **记忆模型 FSRS**：每个 concept 挂记忆状态，quiz/练习事件更新它；可提取性跌破阈值 →
  自动在 briefing 插入复习。FSRS 也替代知识型技能的朴素时间衰减（有认知科学依据）。
