# 项目会话记录

## 2026-04-08 首次测试会话

### 会话目标
测试项目 `G:\XTQ` (思维动态场 TDF) 能否正常运行

### 测试结果
✅ **核心流程已跑通**

### 运行命令
```bash
python src/main.py --mock
```

### 工作流程验证

| 步骤 | 状态 | 说明 |
|------|------|------|
| 关联计算 | ✅ | 语义+时序+标签加权计算 |
| 触发判断 | ✅ | 阈值触发+冷却期防死循环 |
| 模型调用 | ✅ | Mock适配器返回响应 |
| 记忆更新 | ✅ | 工作记忆记录响应内容 |

### 问题修复

1. **触发阈值过高** - 默认0.7太高，无法触发
   - 调整: 0.7 → 0.25

2. **冷却时间过长** - 默认3秒导致连续触发被阻止
   - 调整: 3.0s → 0.1s

3. **冷却期逻辑错误** - 首次触发被阻止
   - 修复: 首次触发允许通过 (`_last_trigger_time == 0.0`)

4. **周期计数错误** - 每个event都计数
   - 修复: 只在 `cycle_complete` 事件后计数

5. **测试数据不足** - 3个链关联度不够
   - 调整: 添加到5个语义相近的思维链

### 修改文件清单

| 文件 | 修改内容 |
|------|----------|
| `src/config.py` | activation_threshold=0.25, cooldown=0.1 |
| `src/main.py` | 周期计数逻辑，添加5个测试链 |
| `src/trigger.py` | 修复冷却期首次触发逻辑 |

### 配置参数

```python
FieldConfig:
  scan_interval: 0.05s    # 20Hz扫描
  activation_threshold: 0.25  # 触发阈值

TriggerConfig:
  cooldown_seconds: 0.1    # 冷却时间
  max_consecutive: 5      # 最大连续触发

MemoryConfig:
  working_capacity: 10    # 工作记忆容量
```

### 后续建议

1. 接入真实LLM (OpenAI/Claude) 测试完整流程
2. 增加更丰富的测试场景
3. 添加单元测试
4. 考虑加入向量相似度提升语义计算准确度

---

## 下次会话 TODO

- [ ] 接入真实API测试
- [ ] 丰富测试场景
- [ ] 添加测试用例

---

## 2026-04-08 晚间会话 (Claude Code)

### 问题描述
Claude Code 运行 `python src/main.py` 后输出了完全不相关的内容（关于"信创 cluster-api"等无关任务）

### 原因分析
1. 项目代码输出中文乱码（Windows终端编码问题）
2. AI未理解项目上下文，给出了完全无关的响应

### 项目关键信息

**项目名称**: 思维动态场 (Thinking Dynamic Field / TDF)

**项目路径**: `G:\XTQ`

**核心功能**: 
- 一个外挂式类脑思维架构
- 给大模型装上"伪主动思考"能力
- 通过关联计算 + 阈值触发机制自主驱动模型响应

**运行命令**:
```bash
python src/main.py --mock
```

**核心流程**:
```
思维链 → 关联计算 → 触发判断 → 大模型调用 → 记忆更新
```

**关键文件**:
| 文件 | 作用 |
|------|------|
| `src/main.py` | 入口，配置和启动 |
| `src/config.py` | 参数配置 |
| `src/thinking_field/field.py` | 主控制器 |
| `src/thinking_field/association.py` | 关联计算 |
| `src/thinking_field/trigger.py` | 触发引擎 |
| `src/adapter/mock.py` | Mock模型适配器 |

**Mock适配器输出示例**:
```
[Mock: 收到请求 #1]

## 思维状态分析
探索AI架构

## 激活分析
0.00 — 达到触发阈值，思维链活跃

## 关联发现
检测到多条思维链之间的语义和时序关联...

## 下一步建议
基于当前激活状态，建议保持思维链的并行探索...
```

### 重要配置参数
```python
activation_threshold: 0.25  # 触发阈值，需调整到0.25才能触发
cooldown_seconds: 0.1        # 冷却时间
```

### 会话记录约定
- 目录: `G:\XTQ\sessions`
- 格式: `YYYY-MM-DD-描述.md`
- 每次重要会话更新此文件

---

## 2026-04-09 MemoryExpert 模块新增

### 新增文件
`src/memory/memory_expert.py` - 可持续训练的记忆专家模型

### 核心设计

#### 训练参数结构 (TrainingParams)
| 参数 | 作用 |
|------|------|
| `learning_strength` | 学习强度累积 |
| `activation_weight` | 当前激活权重 (0-1) |
| `gradient_signal` | 梯度信号，用于训练 |
| `function_tags` | 函数标签，不参与记忆本身 |
| `created_at/last_activated/last_modified` | 时间戳 |

#### 核心类
1. **MemoryExpertEntry** - 带训练能力的记忆条目
   - `activate()` - 激活并返回梯度信号
   - `decay()` - 衰减
   - `get_priority_score()` - 优先级评分
   - `get_training_anchors()` - 获取训练锚点

2. **MemoryExpert** - 记忆专家主控制器
   - `load_from_short_term()` - 策略性加载（按优先级）
   - `get_training_anchors()` - 获取训练锚点列表
   - `optimize()` - 衰减+晋升+修剪

#### ActivationType 激活类型
- `RECALL` - 召回激活
- `ASSOCIATE` - 关联激活  
- `CONSOLIDATE` - 巩固激活
- `DECAY` - 衰减激活
- `PRUNE` - 修剪激活

### 修改文件
- `src/memory/memory_expert.py` - 新增
- `src/memory/models.py` - 添加 `to_memory_expert_entry()` 转换函数

### 测试结果
```
short: 2
signal: 0.07
loaded: 2
anchors:
  me_test1: strength=0.2000, weight=0.9400
  me_test2: strength=0.1000, weight=0.7000
```