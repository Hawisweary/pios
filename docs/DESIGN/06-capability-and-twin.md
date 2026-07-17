# 06 · Capability & Twin

## Skill Engine（防自欺是第一要务）

```
level(skill) = scale( Σ weight(event) × decay(now − event.ts) )
```

证据权重示例：项目上线/被合并 PR 1.0 · 通过抽测/考试 0.7 · 独立习题 0.5 ·
精读并写 summary 0.4 · 听课/被动阅读 0.1。decay 半衰期约 180 天——不用的技能掉级，
这是特性不是 bug。每个 level 同时输出 **confidence**：证据少的技能显示"低置信"。

**校准机制（防通胀关键）**：每月 Review Agent 对涨最快的 2–3 个技能出抽测题（费曼式：
解释 + 手写代码），结果是权重最高的证据之一。没有它，Skill Tree 三个月内变成自我安慰的装饰。

## Capability = Skill 的加权聚合（又一个投影）

```
capability:research = 0.25·math + 0.20·paper-reading + 0.20·writing
                    + 0.20·coding + 0.15·experiment-design
```

"Frontier AI Research 需要 Research 8 / Engineering 7 / Communication 6"比
"Python Level 9"有意义得多。零新存储，只加一层配置。

**必须现在指出的陷阱**：Communication / Leadership 几乎没有自动证据源（GitHub 采不到
"讲清楚了一个概念"）。必须显式定义其证据事件：blog 发布、讲课/答疑、PR review 质量、
小组项目角色。否则这两项永远停在 Level 0，Twin 会系统性把你推向纯技术，违背它们被列入画像的初衷。

## Twin Engine（诚实的数字孪生）

- **role_profile 是手工定义的实体**，不是 AI 幻想。来源：真实 JD + 在职者公开履历 +
  导师建议，每学期修订。每个画像 = 一个 capability 要求向量。
- **匹配度 = 当前 capability 向量对画像要求的加权覆盖率**。这**不是录取概率，是能力画像匹配度**——
  界面必须写清楚。
- **Gap 分析是真正输出**："距 frontier lab 画像，最大缺口是 CUDA(1/6) 和 research(0/3 papers)"。
  gap 列表直接喂给 Learning Engine 成为排课优先级。这就是长期智能的闭环：**目标 → 缺口 → 今日计划**。

探索期可同时维护 2–3 个候选画像，让 Twin 并行算多个匹配度——哪个方向 gap 缩得快，
本身就是方向收敛的证据（无需人为约期硬选）。
