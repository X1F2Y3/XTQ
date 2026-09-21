# Changelog

本仓库所有值得记录的变更都在这里。格式遵循
[Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增
- `LICENSE`（MIT）、`CHANGELOG.md`、`.gitattributes`。
- README 增加「当前状态」与「路线图」章节，区分**已实现**与**规划中**，
  修正原先"项目结构"把未实现文件写成完成时态的问题。

### 变更
- `.gitignore` 补齐 OS / 编辑器 / 测试缓存 / 临时脚本噪音规则。
- README 项目结构树根由绝对路径 `G:\XTQ\` 改为仓库相对路径 `XTQ/`。

### 移除
- 清出散落在仓库根的 14 个临时探针脚本（`test_glm*.js` / `test_*.py` /
  `test_net.ps1` / `glm_*.txt` / `glm_test.json`）—— 均为第三方模型连通性
  试验残留，与 TDF 项目无关。

## [0.1.0] — 2026-04-08

### 新增
- 首个可运行骨架：思维动态场（`thinking_field/`）+ 三层记忆系统（`memory/`）
  + Mock 适配器（`adapter/`）。
- Mock 模式跑通完整链路：扫描 → 关联计算 → 触发判断 → 记忆流转。
- 文档：`PROJECT.md`、`docs/architecture.md`、`docs/conventions.md`、
  `docs/api_reference.md`、`docs/module_design.md`。
- 会话记录：`sessions/2026-04-08-first-test.md`。

[Unreleased]: https://github.com/X1F2Y3/XTQ/commits/main
[0.1.0]: https://github.com/X1F2Y3/XTQ/commit/35c7ea1
