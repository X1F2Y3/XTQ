# 思维动态场 (Thinking Dynamic Field)

## 项目初衷

### 背景

当前主流大模型（基于Transformer架构）本质是**静态的被动响应系统**——输入prompt，输出response。这种架构存在根本性缺陷：

1. **无持续状态**：每次调用都是独立的，没有跨次交互的内在驱动力
2. **无主动触发**：模型不会"自己想说话"，只能被动响应
3. **交互损耗**：人类与AI之间存在大量语义转译，每次转译损失约50%的理解力
4. **不符合直觉**：真正的智能体应该能"自主思考、自主决策、自主行动"

### 目标

构建一个**外挂式动态思维架构**，架起AI神经网络层：

**第一阶段（当前）**：作为外挂给大模型优化提示词和决策逻辑，模拟"伪主动"能力

**第二阶段**：外挂拥有自己的类脑神经架构，具备内部向量/权重、主动思考、自主决策能力

**第三阶段**：不再依赖Transformer模型，外挂本身就是一个完整AGI

### 核心理念

```
不是：  用户 → 大模型 → 响应
而是：  外挂（类脑）→ 大模型（执行器）
```

外挂不是"调用层"，而是"主体"——大模型变成它的手和嘴。

---

## 跨阶段架构对齐策略

### 核心设计原则：抽象层隔离 V1 与 V3 的差异

**识别重构风险**：思维链的"表示方式"在 V1→V3 会发生根本性变化：

| 阶段 | 思维链表示 | 关联计算方式 | 触发方式 |
|------|-----------|-------------|---------|
| V1 外挂期 | 纯文本 + 标签 | 文本相似度 | 固定阈值 |
| V2 混合期 | 文本 + 向量嵌入 | 向量相似度 + 文本 | 动态电位 |
| V3 类脑期 | 纯向量/权重分布 | 向量空间运算 | 类神经元激活 |

**解法**：在 V1 就抽取 `Representation` 抽象协议，控制逻辑不变，只换表示实现：

```python
# 这个抽象接口 V1/V2/V3 不变
class Representation(Protocol):
    def get_features(self) -> Any: ...
    def compute_similarity(self, other) -> float: ...

# V1 实现: TextRepresentation
# V2 实现: HybridRepresentation
# V3 实现: VectorRepresentation

# ThoughtChain 类 V1/V2/V3 不变，只持有 Representation
class ThoughtChain:
    repr: Representation  # 可插拔替换
    # 其他字段不变...
```

### 重构风险矩阵

| 模块 | V1 实现 | V3 实现 | 重构风险 | 对齐策略 |
|------|---------|---------|----------|----------|
| **思维表示** | TextRepresentation | VectorRepresentation | **高** | ✅ V1 抽抽象协议 |
| **关联计算** | AssociationEngine (接口不变) | AssociationEngine (接口不变) | **低** | ✅ 接口固定，内部算法可换 |
| **触发引擎** | ThresholdTrigger | NeuronTrigger | **中** | ✅ 抽象 TriggerPolicy 接口 |
| **记忆系统** | 文本标签分级 | 权重衰减曲线 | **中** | ✅ MemoryEntry 抽象数据接口 |
| **主控制器** | ThinkingField 循环逻辑 | ThinkingField 循环逻辑 | **极低** | ✅ 逻辑完全不变 |
| **模型适配器** | OpenAI/Claude/Mock API | 降为执行器接口 | **低** | ✅ 接口不变，内部简化 |

### V1 → V3 升级路径

```
V1.0 (外挂期)
│
│  替换 TextRepresentation → HybridRepresentation
│  实现 TriggerPolicy 抽象
│
▼
V2.0 (混合期)
│
│  替换 HybridRepresentation → VectorRepresentation
│  记忆系统加入权重衰减
│  大模型 adapter 简化为执行器接口
│
▼
V3.0 (类脑期)
```

**每个阶段需要修改的文件**：

| 升级 | 新增文件 | 修改文件 | 不变文件 |
|------|----------|----------|----------|
| V1→V2 | 2个 | 3个 | 4个 |
| V2→V3 | 1个 | 2个 | 5个 |

---

## 可落地的详细需求

### Phase 1: 基础架构（V1.0 - 当前交付）

#### 1.1 思维动态场（Thinking Dynamic Field）

**定义**：一个持续运行的状态机，维护思维链的活跃状态和关联关系。

```
工作记忆 ──► 关联计算 ──► 触发判断 ──► 请求生成
    │                                          │
    └── 反馈学习 ◄─── 响应结果 ◄── 大模型 ◄─────┘
```

##### 1.1.1 思维链（ThoughtChain）

每个思维链是一个结构化实体：

| 字段 | 类型 | 说明 | V3 变化 |
|------|------|------|---------|
| chain_id | str | 唯一标识符 | 不变 |
| theme | str | 思维主题 | 不变 |
| content | str | 当前思维内容 | 转为向量表示 |
| activation_level | float | 激活强度 0.0-1.0 | 转为类电位值 |
| tags | list[str] | 关联标签 | 转为权重特征 |
| created_at | datetime | 创建时间 | 不变 |
| last_activated | datetime | 最后激活时间 | 不变 |
| activation_count | int | 历史激活次数 | 不变 |

##### 1.1.2 关联计算（Association Engine）

计算思维链之间的关联强度：
- **语义关联**：基于内容的文本相似度
- **时序关联**：相邻激活的思维链自动增强关联
- **标签关联**：共享标签的思维链天然关联

```python
# 关联强度计算
association_strength = (
    semantic_weight * semantic_similarity +
    temporal_weight * temporal_proximity +
    tag_weight * tag_overlap
)  # 结果归一化到 0.0 - 1.0

# 权重默认值
semantic_weight = 0.5   # 语义内容
temporal_weight = 0.3   # 时序距离
tag_weight = 0.2         # 标签重叠
```

##### 1.1.3 触发机制（Activation Trigger）

替代固定60Hz循环，采用**类生物神经元阈值触发**：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| activation_threshold | 0.7 | 激活阈值 |
| cooldown_seconds | 3.0 | 触发冷却时间（防止死循环） |
| max_consecutive_triggers | 5 | 最大连续触发次数 |
| scan_interval | 0.05 | 循环扫描间隔(50ms ≈ 20Hz，可配置) |

**防死循环策略**：
1. 全局冷却期：上次触发后等待 cooldown 秒
2. 连续次数限制：超过最大次数后强制暂停
3. 内容去重：相同思维链不会连续触发
4. 衰减机制：未激活的思维链自然衰减

#### 1.2 记忆管理系统（Memory System）

##### 1.2.1 三层记忆

| 层级 | 容量 | 生命周期 | 沉淀条件 | V3 变化 |
|------|------|----------|----------|---------|
| 工作记忆 | 10条 | 当前会话 | - | 转为动态活跃集 |
| 短期记忆 | 100条 | 会话间保留 | 激活次数>=3 | 加入衰减权重 |
| 长期记忆 | 无上限 | 永久存储 | 激活次数>=10 且 关联度>=0.6 | 转为知识图谱 |

##### 1.2.2 记忆策略

```
新数据 ──► 工作记忆 ──► 短期记忆 ──► 长期记忆
              │            │             │
              ├── 衰减清理  │── 激活次数   ├── 标签沉淀
              └── 去重合并  └── 时间衰减   └── 关联图谱
```

**记忆标签策略**：
- 每次触发响应后，大模型返回的决策结果和优化的思维链
- 自动打标：关联度、时效性、使用价值
- 沉淀逻辑：基于时序、激活次数、关联强度的综合评分

##### 1.2.3 记忆数据模型（V1/V2/V3 兼容）

```python
class MemoryEntry:
    """抽象数据接口，V1/V2/V3 兼容"""
    chain_id: str
    data: Any  # V1=str, V2=Text+Vector, V3=Weights
    created_at: datetime
    strength: float
    accessed_at: datetime
    access_count: int
    tags: list[str]
    metadata: dict  # 扩展字段
```

#### 1.3 大模型交互层（Model Adapter）

##### 1.3.1 非阻塞调用

- 异步调用，不阻塞思维场运行
- 支持多模型（OpenAI、Claude等）
- 状态保持：传递上一次决策结果和优化后的思维链

##### 1.3.2 Prompt构建策略

触发时发送给模型的prompt结构：

```
## 当前思维状态
{活跃思维链}

## 关联分析
{关联强度最高的N条思维链}

## 历史记忆参考
{相关的短期/长期记忆}

## 上次决策结果
{上一次返回的摘要}

## 请执行
{根据当前状态，给出决策和思考}
```

##### 1.3.3 响应处理

模型返回后的处理：
1. 解析响应内容
2. 更新思维链状态（激活/衰减）
3. 评估是否需要沉淀到短期/长期记忆
4. 更新关联图谱

#### 1.4 核心类设计（V3 对齐版）

```
ThinkingField          # 主控制器 (V1/V2/V3 不变)
│
├── ThoughtChain        # 思维链 (V1/V2/V3 不变，内部替换 Representation)
│   └── repr: Representation (V1=Text, V2=Hybrid, V3=Vector)
│
├── AssociationEngine   # 关联计算 (接口不变，内部算法可替换)
│
├── TriggerEngine       # 触发引擎
│   └── policy: TriggerPolicy (V1=Threshold, V3=Neuron)
│
├── MemorySystem        # 记忆管理
│   ├── WorkingMemory
│   ├── ShortTermMemory
│   └── LongTermMemory
│
└── ModelAdapter        # 大模型交互层 (V1=完整API, V3=执行器)
```

### Phase 2: 未来迭代规划

- 内部向量/权重表示（替换 TextRepresentation）
- 类脑注意力机制
- 主动学习/遗忘曲线
- 思维链自我演化

---

## 约束条件

1. 不修改模型本身，纯外部实现
2. 异步非阻塞，不影响正常调用
3. 配置化参数，可快速调优
4. 无外部依赖时可独立运行（Mock模式）
