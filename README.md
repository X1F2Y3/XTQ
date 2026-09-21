# 思维动态场 (Thinking Dynamic Field · TDF)

> 外挂式类脑思维架构 —— 给大模型装上"大脑皮层"

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg?style=flat-square)](https://www.python.org/)
[![Phase](https://img.shields.io/badge/phase-1%20外挂期-orange.svg?style=flat-square)](#演化路径)
[![Status](https://img.shields.io/badge/status-experimental-lightgrey.svg?style=flat-square)](#当前状态)

---

## 一句话

构建一个**外挂式动态思维场**：以通用大模型为「执行器」，在外挂层维护持续的思维状态、
关联结构与主动触发能力，最终演化为**不依赖 Transformer 的类脑架构**。

```
不是：  用户 → 大模型 → 响应
而是：  外挂（类脑主体）→ 大模型（执行器）
```

---

## 当前状态（重要，先读这里）

本仓库是**进行中的个人研究项目（Phase 1 / 外挂期）**，不是可用产品。
请按"实验记录"而非"成熟库"的预期来看待它：

| 维度 | 现状 |
|:--|:--|
| 可运行 | ✅ Mock 模式可跑通完整"扫描 → 触发 → 记忆流转"链路 |
| 真实模型 | 🟡 仅 `MockAdapter` 落地；OpenAI / Claude 适配器为**规划中** |
| 测试 | ❌ **`tests/` 尚未建立**（`docs/conventions.md` 已定义规范，见 [路线图](#路线图)） |
| 稳定性 | 🔴 实验性，接口随时可能变 |

> **诚实标注**：本 README 的「项目结构」反映**仓库实际内容**；尚未实现的部分
> 统一放在 [路线图](#路线图) 章节，不会以完成时态混写进结构树。

---

## 核心假说

当前主流大模型（Transformer）本质是**静态的被动响应系统**：输入 prompt，输出 response。
它缺少三样东西：

1. **持续状态** —— 每次调用彼此独立，没有跨次交互的内在驱动力
2. **主动触发** —— 模型不会"想说话"，只能被动响应
3. **稳定自我表示** —— 没有一个跨会话存续的"我"来决定该激活什么

TDF 的赌注：把这三件事**外挂**在一个普通大模型之上，能否涌现出"伪主动"乃至"类主体"行为。
详见 [PROJECT.md](PROJECT.md) 的项目初衷与 [docs/architecture.md](docs/architecture.md) 的架构设计。

---

## 架构

```
┌───────────────────────────────────────────────────────────┐
│                   思维动态场 (TDF)                          │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │  工作记忆层   │  │  关联计算层   │  │   触发层      │   │
│  │  WorkingMem  │  │ Association  │  │   Trigger     │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                 │            │
│         ▼                 ▼                 ▼            │
│  ┌──────────────────────────────────────────────────┐   │
│  │              记忆优化系统 (Memory)                │   │
│  │   WorkingMemory → ShortTerm → LongTerm           │   │
│  └──────────────────────────────────────────────────┘   │
│                    │                                     │
│                    ▼                                     │
│  ┌──────────────────────────────────────────────────┐   │
│  │              大模型交互层 (Adapter)               │   │
│  │         Mock（已实现） / OpenAI / Claude（规划）    │   │
│  └──────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────┘
```

**跨阶段设计原则**：V1→V3 思维链的「表示方式」会根本性改变（文本 → 向量 → 权重），
但主控制逻辑不变。因此 V1 就抽取四个抽象协议 —— `Representation`、`TriggerPolicy`、
`MemoryEntry`、`ModelAdapter` —— 换实现不改调用方。详见 [docs/architecture.md](docs/architecture.md)。

---

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. Mock 模式运行（无需 API Key，跑通完整链路）
python src/main.py --mock
```

> 真实模型接入（`--provider openai --api-key ...`）尚未实现，见[路线图](#路线图)。

---

## 演化路径

```
Phase 1: 外挂期 (V1.0 ─ 当前)   ← 你在这里
  └─ 优化 prompt + 决策逻辑，模拟"伪主动"能力
     表示：纯文本 + 标签 · 触发：固定阈值 · 记忆：文本分级

Phase 2: 混合期 (V2.0)
  └─ 外挂拥有内部向量 / 权重，不再完全依赖大模型
     表示：文本 + 向量嵌入 · 触发：动态电位 · 记忆：衰减权重

Phase 3: 类脑期 (V3.0)
  └─ 外挂自成为完整的类脑 AGI，大模型降为执行器
     表示：纯向量 / 权重分布 · 触发：类神经元激活 · 记忆：知识图谱
```

---

## 项目结构（与仓库实际内容一致）

```
XTQ/
├── PROJECT.md                 # 项目初衷与详细需求（假说 / 目标 / 约束）
├── README.md                  # 本文件
├── requirements.txt           # Python 依赖
├── LICENSE                    # MIT
├── CHANGELOG.md               # 变更记录
├── .gitignore / .gitattributes
│
├── docs/
│   ├── README.md              # 文档索引
│   ├── architecture.md        # 架构设计（V1→V3 对齐原则、运行流程）
│   ├── conventions.md         # 开发规范（命名 / 类型注解 / 兼容性 / 提交）
│   ├── api_reference.md       # 核心类与方法定义
│   └── module_design.md       # 各模块详细设计
│
├── sessions/
│   └── 2026-04-08-first-test.md   # 首次联调会话记录
│
└── src/
    ├── main.py                # 入口（--mock）
    ├── config.py              # 全部可调参数（dataclass 集中管理）
    │
    ├── thinking_field/        # 思维场核心
    │   ├── field.py           # ThinkingField 主控制器（扫描循环）
    │   ├── chain.py           # ThoughtChain 思维链
    │   ├── association.py     # AssociationEngine 关联计算
    │   └── trigger.py         # TriggerEngine 触发引擎 + 防死循环
    │
    ├── memory/                # 记忆系统
    │   ├── system.py          # MemorySystem 主系统（流转调度）
    │   ├── working.py         # WorkingMemory 工作记忆
    │   ├── short_term.py      # ShortTermMemory 短期记忆
    │   ├── long_term.py       # LongTermMemory 长期记忆
    │   ├── models.py          # MemoryEntry 等数据模型
    │   ├── memory_expert.py   # 记忆专家（沉淀策略）
    │   └── _verify.py         # 记忆模块自检
    │
    ├── adapter/               # 大模型适配层
    │   └── mock.py            # MockAdapter（无需 API Key）
    │
    └── utils/
        ├── similarity.py      # 文本相似度
        ├── logger.py          # 日志
        └── timer.py           # 时序工具
```

---

## 路线图

| 阶段 | 事项 | 状态 |
|:--|:--|:--|
| Phase 1 | `Representation` / `TriggerPolicy` / `MemoryEntry` 抽象协议落地 | 🟡 部分 |
| Phase 1 | `tests/`（`docs/conventions.md` 已定义：单测 + 集成测试，Mock 可跑） | ❌ 待建 |
| Phase 1 | `OpenAIAdapter` / `ClaudeAdapter`（异步非阻塞） | ❌ 待实现 |
| Phase 1 | CI（lint + pytest，push / PR 触发） | ❌ 待建 |
| Phase 2 | `HybridRepresentation` + `NeuronTrigger` + 记忆衰减权重 | ⏳ |
| Phase 3 | `VectorRepresentation` + `SynapseTrigger` + 知识图谱记忆 | ⏳ |

---

## 文档导航

| 文档 | 说明 |
|:--|:--|
| [PROJECT.md](PROJECT.md) | 为什么做、做什么、怎么做；重构风险矩阵与升级路径 |
| [docs/architecture.md](docs/architecture.md) | 完整架构图、运行流程、核心类关系、防死循环机制 |
| [docs/conventions.md](docs/conventions.md) | 项目级开发规范 |
| [docs/api_reference.md](docs/api_reference.md) | 核心类与方法定义 |
| [docs/module_design.md](docs/module_design.md) | 各模块详细设计 |

---

## 约束条件

1. 不修改模型本身，纯外部实现
2. 异步非阻塞，不影响正常调用
3. 配置化参数（`src/config.py`），可快速调优
4. 无外部依赖时可独立运行（Mock 模式）

---

## License

[MIT](LICENSE) © 2026 X1F2Y3
