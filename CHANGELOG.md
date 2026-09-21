# Changelog

本仓库所有值得记录的变更都在这里。格式遵循
[Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 修复（代码质量审计 — 三技能门禁）

按 `backend-quality-gate` / `lean-implementation` / `frontend-design-guard`
三条判据逐文件审计后的修复。**含两处行为变更**，已显式标注。

- **★ 行为变更｜显著性阈值三处不一致**：`long_term.py` 里"高显著性"的判据
  此前有三套表述 —— 注释写 `access>=5 and strength>=0.5`、`consolidate()`
  实际用 `>=2 and >=0.3`、`stats` 又用 `>=5 and >=0.5`。结果是**被增强的
  记忆和统计为高显著性的记忆不是同一批**。现统一为模块常量
  `HIGH_SALIENCE_ACCESS=5` / `HIGH_SALIENCE_STRENGTH=0.5`，`stats`、
  `consolidate`、核心记忆保护（`CORE_ACCESS_THRESHOLD=10`）全部走常量。
  净效果：增强门槛由 2/0.3 **提高到** 5/0.5，即与注释和统计口径对齐。
- **静默数据丢失**：`PseudoPermanentMemory._persist()` 原先把异常吞进
  logger 后返回 `None`，调用方（`add`/`access`/`decay_all`/`consolidate`）
  无从得知数据**根本没落盘** —— `add()` 成功返回，进程一退数据就没了。
  现改为返回 `bool`，并新增 `healthy` 属性 / `stats['healthy']` 字段，
  由 `MemorySystem` 向上暴露。同时改为「先写临时文件 + `os.replace`」的
  原子落盘，避免写一半崩溃产生半截文件。
- **加载失败不再静默降级**：`_load()` 遇到损坏的存档文件时，原先只打一行
  log 就继续在**空库**上运行（用户会误以为"记忆正常，只是没新数据"）。
  现把损坏文件**另存**为 `<path>.corrupt-<ts>` 再报 ERROR，既不丢也不覆盖。
- **配置项形同虚设**：`MemoryConfig.cleanup_threshold` 定义了却没人用 ——
  `working.py` 写死 `0.1`、`short_term.py` 写死 `0.05`。现两者都改走配置
  （新增 `short_cleanup_threshold=0.05`，因为短期记忆比工作记忆更"耐留"，
  阈值本就该更低，不是简单统一）。
- **删除死代码** `src/memory/_verify.py`：`MemoryValidator` 全仓库无任何
  调用方，且其断言在任何**有历史数据的机器上必然失败**（构造
  `PseudoPermanentMemory()` 即读真实存储文件，再断言 `count != 0`），
  是个"只在全新机器上通过"的假测试。
- **Windows 主入口崩溃**：`main.py` 注册 `signal.SIGTERM`，而 Windows
  Python **没有** `SIGTERM`，`python src/main.py` 会在启动时直接
  `AttributeError`。改用 `getattr` 探测后再注册。
- **`--mock` 参数恒为 True**：`action="store_true", default=True` 使参数
  完全无效；且 docstring 承诺的 `--openai` / `--claude` 从未定义。现改为
  `--provider {mock}`，并如实说明只有 mock 可用（未实现的就不承诺）。
- **反序列化不校验**：`ThoughtChainItem.from_dict` 原先
  `for key in cls.__dataclass_fields__: setattr(...)`，会接受任意 dict 键值
  且不做类型检查。现加字段白名单 + 逐字段类型校验，不符时回落默认值并
  发 warning（避免 `activation_level="high"` 一路传染到算术运算才炸）。
- **连续触发限流不生效**：`trigger.py::_check_consecutive_limit` 注释写
  "超出窗口，重置计数"，实际**什么都没做** → `_consecutive_count` 只增不减。
  现补上真正的归零逻辑。
- `long_term.py::stats` / `memory_expert.py` 排序 / `field.py` 关联构建的
  性能与可读性清理（消除重复 `chain_manager.get()` 调用与逐次临时对象分配）。
- docstring 与实现不符者一律修正：`models.py` / `chain.py` 的
  `_generate_*_id()` 声称"确定性ID"实为随机；`PROJECT.md` 承诺的
  `Representation` 抽象协议在代码中不存在。

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
