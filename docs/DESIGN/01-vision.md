# 01 · Vision

## PIOS 是什么

Personal Intelligence Operating System——一个陪伴本科四年（乃至更久）的个人智能操作系统。
默认 Mentor Agent 名为 **Athena**；配套课程体系名为 **BCIC**。

分工：**BCIC 定义"学什么"，PIOS 决定"今天学什么、为什么、学到什么程度、下一步是什么"，
并持续记录与评估成长。**

## 为什么不是 Notion / Todoist / Obsidian

那些工具管理**任务与笔记**。PIOS 管理**一个人的智能资产随时间的演化**：知识、能力、
研究、决策、职业。它不是记录你今天做了什么，而是回答"按当前轨迹，未来的你会是谁，
还缺什么"。这是 Digital Twin（数字孪生），不是 Task Manager。

## 十二层能力 = 同一套数据的投影

最初构想的 12 层（Identity / Curriculum / Knowledge Graph / Research OS / Project OS /
Investment OS / Research Diary / Skill Tree / AI Mentor / Career OS / Weekly Review /
Long-term Intelligence）不是 12 个模块，而是**同一套底层数据的 12 个视图**。
经过三轮设计，全部收敛为：4 张表 + 若干实体类型 + 几个投影公式 + 一组 Agent prompt。
这个收敛本身是设计正确的证据——见 [08-roadmap](08-roadmap.md) 结尾。

## 护城河

不是 Agent、LLM、Dashboard 或 MCP——这些都会被替换。真正不可复制的是
**四年持续积累的高质量事件流 + 知识图谱 + 决策记录 + 能力演化轨迹**。
它只从你开始记录的那天算起，无法回溯补齐。因此 [Constitution](../../Constitution.md)
把数据层锁死为 local-first 纯文本，代码层可随意重写：**数据是资产，代码是耗材**。

## 首页原则

> PIOS 不替你学习，不替你思考，也不替你做决定。
> 它的职责是帮助你更准确地记录事实、组织知识、发现差距、提出建议，
> 并让你的长期成长过程变得可见、可验证、可复盘。

这条原则的技术形态是 Proposal 边界（见 [07](07-mentor-and-proposal.md)）。
