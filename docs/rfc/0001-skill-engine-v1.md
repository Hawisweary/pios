# RFC-0001: Skill Engine v1

- Status: accepted
- Date: 2026-09-10

## Motivation

事件流已有 20+ 条带深度的真实事件（跨 CS61A / ESPM / R4A / 投资 / 研究）。第一次
够得着一个有意义的能力投影：把"你做了什么"变成"你现在会什么、多确信"。这是迈入 Phase 1 的第一步。

## Problem

如何从事件算出每个概念的强度，且：不自欺（读 ≠ 会）、可审计、生疏后重练能自然恢复、
一个事件如何知道自己练了哪些技能。

## Proposal

`pios skills` —— 对**每个概念**（v1 只到概念粒度）算：

```
当前强度 = Σ_events ( depth_weight × verify_bonus × decay )
  depth_weight:  d1=0.1  d2=0.3  d3=0.6  d4=1.0  d5=1.3
  verify_bonus:  quiz/exam ×1.2（外部验证比自测重）
  decay:         0.5^(days_ago / 180)   半衰期 180 天
峰值深度 = max(depth)      # 永久事实，不衰减
置信度   = f(事件数, 深度多样性, 类型多样性) → 0-1 → 低/中/高
```

**重新激活行为**：不存可变数字；每次调用重新求和，每条事件从自身时间戳独立衰减。
新经验以满权重进入，旧（已衰减）证据仍贡献残值 → 生疏后重练比从零快、且有 head start。
"峰值深度"与"当前强度"分开显示：熟练度会掉会恢复，"曾达到过"是永久的。

**事件→技能的来源**：事件手动打的 `entity_ids`（记录时人的判断，读作业公开 spec），
引擎只读不猜。**不**从 note 文字自动提取（非确定性、需 LLM，违反约束）。
v1 简化：一事件一深度，套用到它标的所有概念；靠标签纪律（只标真练到该深度的概念）保持诚实。

**输出**：按学科分组（从同标签 course 推断）、按当前强度排序。列：概念·峰值·当前强度·置信·事件数·最近。
`pios skills --why concept:X`：列出每条支撑事件及其贡献（Article 7 钻取）。

## Data Model

无新表。纯读 `events`。是投影（Article 4/9）：每次现算，删 pios.db 重建后结果一致。

## Constraints（限制）

Article 9 不存分数 · Article 7 每分可钻证据 · Article 3 只读事实 · 不伪造校准等级（防通胀）·
v1 只算概念（capability 聚合=Phase 2）· 确定性/零 LLM/stdlib-only · 衰减不抹杀峰值 · 低证据标低置信。

## Tradeoffs

- 优点：重新激活免费、可审计、诚实（无假等级）、可重建。
- 代价：一事件一深度不够精确（HW 可能对 A 是 d3、对 B 只是 d2）；靠标签纪律弥补。

## Rejected Alternatives

- **0-10 校准等级**：没跑过月度抽测校准就是假精度；留到有校准锚点后（Phase 1 信号③）。
- **从文字自动提取技能**：非确定性 + 需 LLM，违反约束。
- **每概念各自深度**：更准但更复杂；无压力不做（Article 13），列为 Future Work。

## Migration

纯新增，无迁移。

## Future Work

月度抽测校准 → 真 Level · Capability 聚合（Phase 2）· FSRS 记忆衰减 · 每事件每概念独立深度。
