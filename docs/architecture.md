# 架构设计

## V1→V3 对齐原则

**核心风险识别**：思维链的"表示方式"在V1→V3会发生根本变化，但主控制逻辑不变。

```
V1 (外挂期):  TextRepresentation  + ThresholdTrigger  + MemorySystem
V2 (混合期):  HybridRepresentation + NeuronTrigger     + WeightedMemory
V3 (类脑期):  VectorRepresentation + SynapseTrigger    + GraphMemory

不变的抽象层:
  - ThoughtChain 持有 Representation 接口
  - AssociationEngine 持有计算接口
  - TriggerEngine 持有 TriggerPolicy 接口
  - MemorySystem 持有 MemoryEntry 接口
  - ThinkingField 主循环完全不变
```

---

## 整体架构图

```
┌───────────────────────────────────────────────────────────┐
│                    思维动态场 (TDF)                          │
│                                                           │
│  ┌─────────────┐   ┌─────────────┐   ┌──────────────┐   │
│  │  工作记忆层  │──►│  关联计算层  │──►│   触发层      │   │
│  │ WorkingMem  │   │ Association │   │   Trigger     │   │
│  └─────────────┘   └─────────────┘   └──────┬───────┘   │
│                                              │           │
│                                              ▼           │
│  ┌──────────────────────────────────────────────────┐   │
│  │              记忆优化系统 (Memory)                │   │
│  │                                                   │   │
│  │   WorkingMemory → ShortTermMemory → LongTermMem  │   │
│  │   - 标签沉淀    │ - 激活次数沉淀  │ - 图谱构建     │   │
│  └───────────────────────────▲──────────────────────┘   │
│                              │                          │
│                    ┌─────────┴────────────────┐        │
│                    │    大模型交互层 (Adapter)  │        │
│                    │  - OpenAI / Claude / Mock │        │
│                    │  - 异步非阻塞              │        │
│                    │  - 防死循环                │        │
│                    └─────────▲────────────────┘        │
│                              │ (响应结果)              │
└──────────────────────────────┴───────────────────────────┘
```

## 运行流程

```
1. 思维场启动
   └── 加载长期记忆 → 初始化工作记忆 → 启动扫描循环

2. 扫描循环 (动态频率)
   └── 计算所有思维链的关联强度
       └── 超过阈值？
           ├── 是 → 触发判断
           │   ├── 在冷却期？→ 跳过
           │   ├── 超限触发？→ 跳过
           │   └── 通过 → 生成请求 → 调用大模型
           │       └── 解析响应 → 更新记忆 → 更新关联
           └── 否 → 衰减低关联链 → 继续循环

3. 记忆沉淀
   └── 工作记忆中的数据根据激活次数、时序、关联强度
       自动流转到短期记忆和长期记忆
```

## 核心类关系

```
ThinkingField (主控制器)
├── thought_chains: list[ThoughtChain]
├── association_engine: AssociationEngine
├── trigger_engine: TriggerEngine
├── memory_system: MemorySystem
└── model_adapter: ModelAdapter

AssociationEngine (关联计算)
├── compute_semantic() → float
├── compute_temporal() → float
├── compute_tag_overlap() → float
└── compute_total() → float

TriggerEngine (触发引擎)
├── should_trigger() → bool
├── generate_request() → dict
├── check_cooldown() → bool
└── check_limit() → bool

MemorySystem (记忆系统)
├── working_memory: WorkingMemory
├── short_term_memory: ShortTermMemory
├── long_term_memory: LongTermMemory
└── optimize() → None
```

## 防死循环机制

```
触发请求前检查:
├── cooldown_ok? (距离上次触发 > cooldown_seconds)
├── consecutive_ok? (连续触发次数 < max_consecutive_triggers)
└── content_unique? (当前思维链不是上次的)

触发后:
└── last_trigger_time = now()
└── consecutive_count += 1
└── last_triggered_chain_id = chain_id

重置:
└── 连续触发间隔 > reset_window → consecutive_count = 0
```

## 记忆流转策略

```
新数据 ──► WorkingMemory
                │
                ├── 激活次数 >= 3 ──► ShortTermMemory
                │                           │
                │                           ├── 激活次数 >= 10
                │                           └── 且关联度 >= 0.6
                │                           │
                │                           ▼
                │                     LongTermMemory
                │
                └── 衰减因子: 每次扫描降低 0.05
                └── 清理条件: 强度 <= 0.1 且 在记忆中超过 300 秒
```
