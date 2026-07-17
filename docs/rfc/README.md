# PIOS RFC（How 层）

RFC = **一个设计决策的历史记录**，不是项目初始化清单。三层文档体系里最底、最活跃的一层：

```
Constitution   Why & 不可违背（改宪法要走 Decision + 90 天复盘）
DESIGN/        What（现在的系统设计）
rfc/           How（为什么从旧设计变成新设计 —— 一次一篇，按需生长）
```

## 什么时候写 RFC

发生**改变既有设计的非平凡决定**时才写。例如：换 FSRS 参数模型、events 表加字段、
把某引擎的算法换掉、引入新的实体类型。琐碎改动、纯实现细节、能一句话说清的不写。

**不写 RFC 的情形**：Phase 0 当前的东西已由 DESIGN/ 覆盖，无需追认 RFC。
第一篇 RFC 应在第一个真实的架构**变更**出现时诞生，而不是现在为已有设计补写。

## 与 decision 实体的关系

技术设计决策，对单人开发者本质上就是一个 `decision`。区别：影响**系统架构**的写 RFC
（放这里，供未来的你和 AI 读懂"为什么这样实现"）；影响**你个人成长/职业**的写 decision 实体
（放 vault，进 Twin 与 Calibration）。拿不准就写 decision——它有复盘机制。

## 编号与状态

- 文件名：`0001-event-store-sharding.md`，四位递增编号 + 短横线描述。
- 状态流转：`draft → accepted → (superseded by NNNN)`。RFC 不删除，被取代时标注指向新篇。

## 模板

```markdown
# RFC-NNNN: 标题

- Status: draft / accepted / superseded-by-NNNN
- Date: YYYY-MM-DD

## Motivation        为什么现在需要改
## Problem           当前设计的具体不足
## Proposal          新设计
## Data Model        涉及的表/实体/边变化（如有）
## Examples          具体例子
## Tradeoffs         得失
## Rejected Alternatives   考虑过但放弃的方案，及原因
## Migration         如何从旧状态迁移（事实层不可变——通常是新增而非修改）
## Future Work       留待以后
```

模板致谢 Rust RFC 传统。保持每篇 RFC 聚焦单一决策——一篇讲清一件事。
