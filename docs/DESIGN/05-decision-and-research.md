# 05 · Decision & Research（Decision 对象）

## Decision OS

选课、买电脑、接 offer、投资、创业——同一个 schema。别人没有的两样东西：

- **假设显式化 + 置信度**：每条假设可证伪、标 confidence。复盘时不是问"结果好不好"，
  而是逐条问"哪条假设错了"。决策质量 ≠ 结果质量（好决策可能坏结果），只有假设级复盘能区分。
- **强制预约复盘**：`review_at` 到期，Mentor 自动催办。

```yaml
type: decision
domain: investment / course / career / purchase / research / life
options / chosen / evidence
assumptions: [{claim, confidence}]   # 可证伪
review_at: YYYY-MM-DD
outcome / reflection                 # 复盘时填
```

## 校准引擎（Calibration Engine）

积累几十个决策后，对比"你标 80% 置信的假设，实际对了多少"。**Brier score 随时间的变化 =
判断力这个终极 capability 的量化**，比任何技能分数更深刻，且必须从第一天记录才能在第三年产生价值。
——所以 decision schema 属于 Phase 0，数据不可回溯。

## Research Memory：Idea

Idea 是一等实体，生命周期 `seed → developing → merged / promoted / dead`。
**永不自动合并**——夜间任务用 embedding 找相近 idea，只生成 `merge_idea` 提案由你确认；
静默合并会杀死研究直觉（两个 idea 的"相似"可能正是有价值的差异所在）。
四年后"哪类 idea 最终活了"是研究品味的量化。

## Scientific Memory：Experiment（负结果一等公民）

所有科研工具都丢掉负结果，而它恰是研究品味的来源。`experiment` 实体：

```yaml
type: experiment
idea: idea:xxx
hypothesis / method / dataset / result
status: positive / negative / inconclusive   # negative 与 positive 完全平权
lessons                                        # 负结果最重要的字段
spawned: [idea:yyy]                            # 失败孵化的新 idea
```

Weekly Review 里"本周否证了什么"和"本周完成了什么"并列出现。四年后 Research Graph
里最有价值的路径，很可能是几条穿过 negative 节点的路径。
