# 贡献指南

TDF 是一个**进行中的研究项目**，不是成熟产品。欢迎参与，但请先理解它的定位。

## 在动手之前

读完这三份文档，它们决定了代码怎么写：

1. [PROJECT.md](PROJECT.md) —— 项目假说、目标、重构风险矩阵
2. [docs/architecture.md](docs/architecture.md) —— V1→V3 对齐原则
3. [docs/conventions.md](docs/conventions.md) —— 命名 / 类型注解 / 兼容性 / 提交规范

## 最重要的一条：抽象层优先

V1→V3 思维链的「表示方式」会根本变化（文本 → 向量 → 权重），但**主控制逻辑不变**。
所以任何新功能都必须先问：

> 这东西属于「表示层 / 触发策略 / 记忆数据 / 适配器」中的哪一层？
> 它能不能挂在一个**已有抽象协议**后面，而不是塞进 `ThinkingField` 主循环？

- 新的表示 → 实现 `Representation` 协议，**不改调用方**
- 新的触发策略 → 实现 `TriggerPolicy` 基类，**不改主循环**
- 新的记忆类型 → 走 `MemoryEntry` 接口，V2/V3 只扩展 `metadata`
- 新的模型后端 → 实现适配器接口（对齐 `adapter/mock.py` 的形状）

**反例（会被要求重写）**：把 `if provider == "openai"` 分支写进 `field.py`。

## 不硬编码

沉淀条件、阈值、权重全部走 `src/config.py` 的 dataclass。流转逻辑里**不得出现魔数**。

```python
# 好
if entry.activation_count >= cfg.memory.long_promote_count:
    ...

# 差
if entry.activation_count >= 10:
    ...
```

## 提交前自检

```bash
python -m compileall -q src          # 语法
python src/main.py --mock            # Mock 链路能跑通
```

> 测试套件尚在建设中（见 README 路线图）。**新增模块时请一并补上对应单测** ——
> `docs/conventions.md` 已写明"每个模块必须有对应的单元测试，Mock 模式可跑全部测试"。

## 提交信息

Conventional Commits，祈使句：

```
feat(thinking_field): add TriggerPolicy abstraction
fix(memory): stop promoting entries on decay
docs(architecture): clarify V2 representation swap
```

## 许可

贡献即表示同意以 MIT 许可发布（见 [LICENSE](LICENSE)）。
