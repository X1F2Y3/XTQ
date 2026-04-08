# 思维动态场 (Thinking Dynamic Field - TDF)

> 外挂式类脑思维架构 —— 给大模型装上"大脑皮层"

## 一句话描述

构建一个外挂式的动态思维场，以大模型为执行器，赋予其伪主动思考与决策能力，并最终演化为独立的类脑AGI架构。

## 文档导航

| 文档 | 路径 | 说明 |
|------|------|------|
| 项目初衷与详细需求 | [PROJECT.md](PROJECT.md) | 为什么做、做什么、怎么做 |
| 架构设计 | [docs/architecture.md](docs/architecture.md) | 完整架构图与模块设计 |
| 开发规范 | [docs/conventions.md](docs/conventions.md) | 项目级开发规范 |
| API参考 | [docs/api_reference.md](docs/api_reference.md) | 核心类与方法定义 |
| 模块设计 | [docs/module_design.md](docs/module_design.md) | 各模块详细设计文档 |

## 核心架构

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
│  │    OpenAI / Claude / 任意模型                      │   │
│  └──────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────┘
```

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 运行（Mock模式，无需API Key）
python src/main.py --mock

# 接入真实大模型
python src/main.py --provider openai --api-key YOUR_KEY
```

## 演化路径

```
Phase 1: 外挂期 (V1.0 ─ 当前)
  └─ 优化prompt + 决策逻辑，模拟伪主动能力

Phase 2: 混合期 (V2.0)
  └─ 外挂拥有内部向量 / 权重，不再完全依赖大模型

Phase 3: 类脑期 (V3.0)
  └─ 外挂自成为完整的类脑AGI，大模型降为执行器
```

## 项目结构

```
G:\XTQ\
├── PROJECT.md              # 项目初衷与详细需求
├── README.md               # 本文件
├── requirements.txt        # Python 依赖
├── .gitignore              # Git 忽略规则
├── docs/                   # 文档目录
│   ├── architecture.md     # 架构设计
│   ├── conventions.md      # 开发规范
│   ├── api_reference.md    # API 参考
│   └── module_design.md    # 模块详细设计
│
├── src/                    # 源代码
│   ├── __init__.py
│   ├── main.py             # 入口
│   ├── config.py           # 配置管理
│   │
│   ├── thinking_field/      # 思维动态场核心
│   │   ├── __init__.py
│   │   ├── field.py        # ThinkingField 主控制器
│   │   ├── chain.py        # ThoughtChain 思维链
│   │   ├── association.py  # AssociationEngine 关联计算
│   │   └── trigger.py      # TriggerEngine 触发引擎
│   │
│   ├── memory/             # 记忆管理系统
│   │   ├── __init__.py
│   │   ├── system.py       # MemorySystem 主系统
│   │   ├── working.py      # WorkingMemory  工作记忆
│   │   ├── short_term.py   # 短期记忆
│   │   ├── long_term.py    # 长期记忆
│   │   └── models.py       # 记忆数据模型
│   │
│   ├── adapter/            # 大模型适配层
│   │   ├── __init__.ps
│   │   ├── base.py         # BaseAdapter 抽象基类
│   │   ├── openai_adp.py   # OpenAI适配器
│   │   ├── claude_adp.py   # Claude适配器
│   │   └── mock.py         # Mock适配器（测试用）
│   │
│   └── utils/              # 工具函数
│       ├── __init__.py
│       ├── similarity.py   # 文本相似度计算
│       └── logger.py       # 日志工具
│       └── timer.py        # 时序工具
│
└── tests/                  # 测试
    ├── __init__.py
    ├── test_chain.py       # 思维链测试
    ├── test_association.py # 关联计算测试
    ├── test_trigger.py     # 触发引擎测试
    ├── test_memory.py      # 记忆系统测试
    └── test_integration.py # 集成测试
```

