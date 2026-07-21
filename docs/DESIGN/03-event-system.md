# 03 · Event System（Memory 与 Action 的底座）

## events 表

append-only，是 Memory 和 Action 两个核心对象的物理载体。

```
id · ts · kind · source · entity_ids · depth · payload
```

- `kind`：commit / paper_read / exercise / lecture / quiz / trade / journal /
  decision / idea / experiment / belief_revision / review_recall / milestone …
- `depth`：证据深度 1–5（见 [04](04-knowledge-graph.md) 证据阶梯），不适用则空。
- 事实源是 `vault/events/YYYY/MM.jsonl`（按月分片的 JSONL，在私有仓库里）；`events` 表是它的可查询镜像。

## 三个例子吃下所有场景

- **学习**：读完 FlashAttention → 一条 `paper_read` 事件，Graph Engine 自动补边，
  Skill Engine 给 transformer 加证据。
- **投资**：买入 NVDA → 一条 `trade` 事件，payload 是 thesis；一年后 Review Agent
  把"当时决策 + 之后走势"拼成 decision review——零额外结构。
- **项目**：给 nanoGPT 提交 → `commit` 事件，同时是项目进度和 python/transformer 的高权重证据。

## Vault（文档层）

每个实体一个 Markdown 文件，`[[双链]]` 就是图谱边的人类可读形式（Obsidian 兼容）。
纯文本 + git，保证四年后即使 PIOS 代码全部重写，知识资产依然完整可读（Constitution Article 6）。

## pios.db 是派生索引

`events` / `entities` / `edges` / `proposals` 四张表全部可由 JSONL + Vault 重建。
数据库随时可删，`pios rebuild` 重算。

## Time Machine 是免费的

因为事件流 append-only：
- `pios replay 2027-04` = 查询该月事件 + Agent 叙事化；
- "当时的技能树" = 把事件流回放到该时点重算 Skill Engine；
- "当时为什么" = 关联那个月的 journal 与 decisions。

不需要任何新基础设施——这是坚持 append-only 的直接回报，也是架构正确性的证明。

## L0 采集

每个 collector 就是"拉数据 → 写 events"的 ~50 行脚本（GitHub API / arXiv / Zotero /
券商导出）。原则：**默认自动采集，手动输入只保留日记和投资 thesis 这两样本就该手写的东西。**
自然语言入口 `pios say` 降低手动记录摩擦。
