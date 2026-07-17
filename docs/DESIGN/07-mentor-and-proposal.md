# 07 · Mentor & Proposal

## Athena：唯一的对话主体

Mentor Agent 每天早上被 cron 唤醒，读取：昨日事件 → 技能变化 → gap 排序 → 复习队列，
生成 Daily Briefing（"Good Morning Harry，今天 Probability 45min / Transformer 2h …"）。
工具：查图谱、查事件、写计划、出抽测题、调 Research Agent。prompt 见
`agents/mentor/BRIEFING_PROMPT.md`。

**Weekly Review / Resume 生成不是独立功能**：同一套查询换 7 天窗口 + 对比上周 = 周报；
`type=project/paper` 的实体 + 高证据事件 = 简历素材库。

## 推理回路（L3.5 Reflection Pass）

推理能力在模型里，不需要建"推理引擎"。要建的是推理的**输入结构**（图谱查询）和**输出容器**（Proposal）：

夜间批处理发现"Probability→Optimization→Transformer 的轨迹指向 FlashAttention，
而它需要 CUDA" → 生成 `reschedule` 提案，附完整推理链 → 你早上一键批准，课表才真的改。

## Proposal 边界（整个系统最重要的一条线）

> Event = 真实发生。Proposal = AI 建议。Accept = 用户意志。

AI 的一切主动性以 Proposal 形式落库，等待批准（Constitution Article 3）。
**Proposal 本身就是事实**——"AI 在某时刻提出过某建议、你接受或拒绝了它"和"你读了一篇论文"
没有本质区别，只是行为主体是 AI。所以两态模型零例外：

```
proposals 表：pending → accepted / rejected / expired
```

被拒绝的提案连同理由永久保存——你的"不"和"是"一样是资产。副产品：proposals 表成为
"AI 建议质量"的记录，四年后可回答"Athena 的建议我采纳了多少、效果如何"（成长价值代理指标）。

## Curiosity Engine（唯一不是 Task 的引擎）

发现"与近期活跃簇相邻、但事件数为零的边界节点"，生成 `exploration` 提案。

**写死的纪律**：exploration 提案**永远不进课表、不计完成率**，在 briefing 单列"发现"区。
它是启发不是任务——一旦好奇心被调度器接管变成待办，这个引擎就死了，还会连累整个系统令人厌恶。
