# 模块详细设计

## V3 对齐设计

### V1→V3 兼容性保证

本模块设计在 V1 阶段就预留了抽象层，确保 V2/V3 升级时只替换实现，不修改调用方。

```
抽象层 (不变)          V1 实现              V2 实现              V3 实现
─────────────          ───────              ───────              ───────
Representation     TextRetrieval        HybridRep            VectorRep
TriggerPolicy      ThresholdPolicy      NeuronPolicy         SynapsePolicy
MemoryEntry        TextEntry            WeightedEntry        GraphEntry
ModelAdapter       ModelAPI             ModelAPI             ExecutorPort
```

---

## 模块清单

### 1. ThinkingField (主控制器)

**职责**: 运行思维场主循环，协调各模块

**核心逻辑**:
```
1. 加载长期记忆 → 初始化工作记忆
2. 循环:
   a. 计算所有思维链的关联强度
   b. 关联强度 > 阈值?
      - 是: 检查触发条件(冷却/次数/去重) → 通过则调用大模型
      - 否: 衰减低关联链
   c. 解析大模型响应 → 更新记忆 → 更新关联
   d. 记忆沉淀(工作→短期→长期)
3. 结束: 保存长期记忆
```

**V3 不变**：整个循环逻辑

### 2. ThoughtChain (思维链)

**职责**: 表示单条思维链

**内部表示 (V3 可替换)**:
```python
class ThoughtChain:
    chain_id: str
    theme: str
    repr: Representation  # ← 这里可以换实现
    activation_level: float
    created_at: datetime
    last_activated: datetime
    activation_count: int
```

### 3. AssociationEngine (关联计算)

**职责**: 计算思维链之间的关联强度

**V1 实现**:
- 语义: 文本Jaccard相似度
- 时序: 时间衰减函数
- 标签: 重叠标签数 / 总标签数

**V3 升级**: 内部使用向量相似度，但接口不变

### 4. TriggerEngine (触发引擎)

**职责**: 判断是否触发触发请求，并生成prompt

**V1 策略**: 固定阈值 + 冷却 + 次数限制
**V3 策略**: 类神经元激活电位，但通过 `TriggerPolicy` 接口，ThinkingField 不感知变化

### 5. MemorySystem (记忆管理)

**职责**: 管理三层记忆，负责数据流转和优化

**V1 实现**: 文本 + 标签
**V3 升级**: 权重衰减 + 图谱，但通过 `MemoryEntry` 接口，调用方不感知变化

### 6. ModelAdapter (大模型交互层)

**职责**: 封装各种大模型 API

**V1 提供**: OpenAI / Claude / Mock 适配器
**V3 升级**: 降为执行器接口，内部简化，接口形式不变
