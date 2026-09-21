"""配置管理 - 集中管理所有可调参数"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class FieldConfig:
    """思维场全局配置"""
    scan_interval: float = 0.05          # 扫描间隔(秒) ~20Hz
    activation_threshold: float = 0.10   # 激活阈值
    semantic_weight: float = 0.5         # 语义关联权重
    temporal_weight: float = 0.3         # 时序关联权重
    tag_weight: float = 0.2              # 标签关联权重


@dataclass
class TriggerConfig:
    """触发引擎配置"""
    cooldown_seconds: float = 0.1        # 全局冷却时间
    max_consecutive: int = 20             # 最大连续触发次数
    reset_window: float = 0.5           # 连续计数重置窗口(秒)
    decay_factor: float = 0.05           # 每次扫描衰减因子


@dataclass
class MemoryConfig:
    """记忆系统配置"""
    working_capacity: int = 10           # 工作记忆容量
    short_capacity: int = 100            # 短期记忆容量
    short_promote_count: int = 1         # 晋升到短期记忆的激活次数
    long_promote_count: int = 3         # 晋升到长期记忆的激活次数
    long_min_association: float = 0.6    # 长期记忆最低关联度
    working_decay: float = 0.05          # 工作记忆衰减因子
    cleanup_threshold: float = 0.1       # 清理阈值(强度低于此被清除)
    cleanup_timeout: float = 300.0       # 清理超时(秒)


@dataclass
class TDFConfig:
    """思维动态场完整配置"""
    field_config: FieldConfig = field(default_factory=FieldConfig)
    trigger: TriggerConfig = field(default_factory=TriggerConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    model_provider: str = "mock"         # mock / openai / claude
    model_api_key: str = ""
    model_name: str = ""
