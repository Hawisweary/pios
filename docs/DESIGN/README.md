# PIOS Design（Master Plan · What 层）

这是 PIOS 的系统设计文档——三层文档体系的中间层。

```
Constitution.md   Why & 不可违背   —— 极少改（最高法）
docs/DESIGN/      What（系统全景）  —— 缓慢演进（本目录）
docs/rfc/         How（每个决策）   —— 持续迭代，一次一篇
docs/PRINCIPLES.md  设计哲学速查（四对象/两态/证据阶梯/成功标准/死亡陷阱）
```

一小时读完全部八章即可重新装载整个 PIOS 的设计。各章只讲"是什么、为什么这样"，
不放实现细节；实现细节属于代码和 RFC。

## 目录

1. [Vision — PIOS 是什么，为什么不是待办清单](01-vision.md)
2. [Architecture — 三条公理、分层、两种状态](02-architecture.md)
3. [Event System — Memory 与 Action 的底座](03-event-system.md)
4. [Knowledge Graph — 图谱、知识演化、证据深度、学习引擎](04-knowledge-graph.md)
5. [Decision & Research — 决策 OS、校准、Idea 与 Experiment](05-decision-and-research.md)
6. [Capability & Twin — 技能、能力聚合、数字孪生与差距](06-capability-and-twin.md)
7. [Mentor & Proposal — Athena、推理回路、AI/人边界](07-mentor-and-proposal.md)
8. [Roadmap — 四阶段、触发条件、护城河](08-roadmap.md)

## 维护约定

- 章节文件名用连字符（`01-vision.md`），便于 git 与工具处理。
- 一章长到难以一口气读完（约 >200 行）时，才考虑再拆；在那之前不拆。
- 任何改变既有设计的决定，先写 RFC，再回来更新对应章节——DESIGN 记录"现在的设计"，
  RFC 记录"为什么从旧设计变成新设计"。
