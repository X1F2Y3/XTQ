# 开发规范

## 代码规范

### 命名
- 类名：`PascalCase`（`ThoughtChain`, `AssociationEngine`）
- 函数/变量：`snake_case`
- 常量：`UPPER_SNAKE_CASE`
- 私有方法：`_leading_underscore`

### 文件结构
```python
"""模块描述"""
from __future__ import annotations
import ...

# 常量定义
CONSTANT_X = 1.0

# 数据模型 / Pydantic 模型
class ...

# 业务逻辑
class ...

# 入口 / 演示
if __name__ == "__main__":
    ...
```

### 类型注解
所有公共函数必须有类型注解和返回值说明。

## V1→V3 兼容性规范

### 新增表示层必须遵守
- 新 `Representation` 实现必须符合 `Protocol` 接口
- 替换实现时**不得修改调用方**代码
- `ThoughtChain` 类只通过接口交互，不关心内部实现

### 新增触发策略必须遵守
- 新 `TriggerPolicy` 实现必须继承 `TriggerPolicy` 基类
- 替换策略时**不得修改 ThinkingField** 主循环

### 记忆数据必须遵守
- `MemoryEntry` 接口不变，V2/V3 扩展 `metadata` 字段
- 沉淀条件可配置，**不硬编码在流转逻辑中**

## 测试规范
- 每个模块必须有对应的单元测试
- 集成测试覆盖完整触发链路
- Mock 模式无需 API Key 可运行全部测试

## 提交规范
- `feat:` 新功能
- `fix:` 修复
- `refactor:` 重构（不改变行为）
- `docs:` 文档
