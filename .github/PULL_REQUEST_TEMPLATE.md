## 这个 PR 做什么

<!-- 一两句。引用了哪个 issue？ -->

Closes #

## 抽象层优先（本项目的核心约束）

见 README「最重要的一条：抽象层优先」与 `docs/conventions.md`：

- [ ] 新功能挂在了已有抽象协议后面（`Representation` / `TriggerPolicy` /
      `MemoryEntry` / `ModelAdapter`），而不是塞进 `ThinkingField` 主循环
- [ ] 没有把 `if provider == "openai"` 这类分支写进 `field.py`
- [ ] 阈值 / 权重 / 沉淀条件走 `src/config.py` 的 dataclass，**流转逻辑里没有魔数**

## 验证

```bash
python -m compileall -q src     # 语法
python src/main.py --mock       # Mock 链路跑通
```

- [ ] 语法通过
- [ ] Mock 链路跑通（贴关键日志行）

## 测试

`tests/` 尚在建设中（见 README 路线图）。`docs/conventions.md` 要求
「每个模块必须有对应的单元测试」——

- [ ] 本 PR 为新增模块补了单测
- [ ] 或（仅限文档 / 非功能改动）不涉及行为变化

## 备注
