# API 参考

## V3 对齐说明

本 API 参考基于 V1 实现，但**所有接口设计已考虑 V2/V3 兼容性**。

抽象接口（不随版本变化）：
- `Representation` - 思维表示协议
- `TriggerPolicy` - 触发策略协议
- `MemoryEntry` - 记忆数据接口
- `ModelAdapter` - 模型交互协议

具体实现（可随版本替换）：
- `TextRepresentation` / `HybridRepresentation` / `VectorRepresentation`
- `ThresholdTrigger` / `NeuronTrigger` / `SynapseTrigger`
- `MemorySystem(V1)` / `WeightedMemory(V2)` / `GraphMemory(V3)`
- `ModelAdapter(V1)` / `ExecutorAdapter(V3)`

---

## 核心类

### `ThinkingField`

主控制器。V1/V2/V3 完全不变。

```python
class ThinkingField:
    def __init__(self, config: FieldConfig) -> None
    async def start(self) -> None
    async def stop(self) -> None
    def add_chain(self, chain: ThoughtChain) -> None
    def remove_chain(self, chain_id: str) -> None
    def get_active_chains(self) -> list[ThoughtChain]
    def get_all_associations(self) -> list[Association]
```

### `ThoughtChain`

V1/V2/V3 类接口不变，内部表示可替换。

```python
class ThoughtChain:
    def __init__(self, theme: str, content: str, ...,
                 representation: Representation | None = None) -> None
    def activate(self) -> None
    def decay(self, factor: float = 0.05) -> None
    @property
    def repr(self) -> Representation  # V1=Text, V2=Hybrid, V3=Vector
```

### `AssociationEngine`

接口不变，内部算法可替换。

```python
class AssociationEngine:
    def __init__(self, weights: WeightsConfig) -> None
    def compute(self, chain_a: ThoughtChain, chain_b: ThoughtChain) -> float
    def compute_semantic(self, a: ThoughtChain, b: ThoughtChain) -> float
    def compute_temporal(self, a: ThoughtChain, b: ThoughtChain) -> float
    def compute_tag_overlap(self, a: ThoughtChain, b: ThoughtChain) -> float
```

### `TriggerEngine`

```python
class TriggerEngine:
    def __init__(self, config: TriggerConfig) -> None
    def should_trigger(self, association: float, chain_id: str) -> bool
    def generate_request(self, chain: ThoughtChain, context: dict) -> dict
    def record_trigger(self, chain_id: str) -> None
    def reset_consecutive(self) -> None
```

### `MemorySystem`

```python
class MemorySystem:
    def __init__(self, config: MemoryConfig) -> None
    def add_to_working(self, entry: MemoryEntry) -> None
    def promote_to_short(self, chain_id: str) -> bool
    def promote_to_long(self, chain_id: str) -> bool
    def get_relevant(self, theme: str, limit: int = 5) -> list[MemoryEntry]
    def optimize(self) -> None
```

### `ModelAdapter` (V3 降为执行器)

V1=完整API，V3=执行器，接口形式不变。

```python
class BaseAdapter:
    async def send(self, prompt: str, context: dict) -> str

class OpenAIAdapter(BaseAdapter): ...
class ClaudeAdapter(BaseAdapter): ...
class MockAdapter(BaseAdapter): ...
```

## 配置

```python
@dataclass
class FieldConfig:
    scan_interval: float = 0.05
    activation_threshold: float = 0.7
    semantic_weight: float = 0.5
    temporal_weight: float = 0.3
    tag_weight: float = 0.2

@dataclass
class TriggerConfig:
    cooldown_seconds: float = 3.0
    max_consecutive: int = 5
    reset_window: float = 30.0
    decay_factor: float = 0.05

@dataclass
class MemoryConfig:
    working_capacity: int = 10
    short_capacity: int = 100
    short_promote_count: int = 3
    long_promote_count: int = 10
    long_min_association: float = 0.6
    working_decay: float = 0.05
    cleanup_threshold: float = 0.1
    cleanup_timeout: float = 300.0
```
