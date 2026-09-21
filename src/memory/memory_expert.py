"""记忆专家模型 - 可持续训练的记忆算法

核心设计:
- 学习强度 (learning_strength): 记忆被激活时的学习强度累积
- 激活权重 (activation_weight): 当前激活状态权重
- 时间戳 (timestamps): 创建/访问/修改时间戳
- 函数标签 (function_tags): 锚点标签，不参与记忆本身，只用于训练优化

记忆流转策略:
- 短期记忆池 → 按学习强度+激活权重 策略加载
- 记忆优化锚点用于训练算法的梯度计算
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
from enum import Enum
import time
import math
import random
import string


PREFIX_MEMORY_EXPERT = "me"


def _generate_expert_id() -> str:
    """生成记忆专家条目ID"""
    chars = string.ascii_lowercase + string.digits
    suffix = ''.join(random.choices(chars, k=8))
    return f"{PREFIX_MEMORY_EXPERT}_{suffix}"


class MemoryStage(Enum):
    """记忆阶段"""
    WORKING = "working"      # 工作记忆
    SHORT_TERM = "short"    # 短期记忆
    LONG_TERM = "long"      # 长期记忆
    CONSOLIDATED = "consolidated"  # 已巩固


class ActivationType(Enum):
    """激活类型 - 函数标签"""
    RECALL = "recall"           # 召回激活
    ASSOCIATE = "associate"     # 关联激活
    CONSOLIDATE = "consolidate" # 巩固激活
    DECAY = "decay"             # 衰减激活
    PRUNE = "prune"             # 修剪激活


@dataclass
class TrainingParams:
    """训练参数 - 用于模型训练的锚点
    
    这些参数不参与记忆内容本身，只用于训练算法进行记忆优化
    """
    learning_strength: float = 0.0    # 学习强度累积
    activation_weight: float = 0.5     # 当前激活权重 (0-1)
    gradient_signal: float = 0.0      # 梯度信号 (用于训练)
    
    # 时间戳
    created_at: float = field(default_factory=time.time)
    last_activated: float = field(default_factory=time.time)
    last_modified: float = field(default_factory=time.time)
    
    # 函数标签 - 激活参数标记 (不参与记忆本身)
    function_tags: list[str] = field(default_factory=list)
    activation_history: list[dict] = field(default_factory=list)
    
    # 训练元数据
    training_count: int = 0
    decay_rate: float = 0.95  # 遗忘曲线衰减率


@dataclass
class MemoryExpertEntry:
    """记忆专家条目 - 带训练能力的记忆条目
    
    整合了记忆内容和训练参数
    """
    # 记忆内容
    entry_id: str
    chain_id: str
    data: Any
    content_hash: str = ""  # 内容哈希，用于去重
    
    # 记忆元数据
    stage: MemoryStage = MemoryStage.WORKING
    tags: list[str] = field(default_factory=list)
    importance: float = 0.5  # 重要性评分
    
    # 训练参数
    training: TrainingParams = field(default_factory=TrainingParams)
    
    def activate(self, activation_type: ActivationType = ActivationType.RECALL) -> float:
        """激活记忆，返回激活强度
        
        1. 更新激活权重
        2. 记录激活历史
        3. 增强学习强度
        """
        now = time.time()
        
        # 计算时间衰减
        time_delta = now - self.training.last_activated
        recency_factor = math.exp(-time_delta / 300)  # 5分钟半衰期
        
        # 更新激活权重
        base_weight = self.training.activation_weight
        self.training.activation_weight = min(1.0, base_weight * 1.2 + 0.1)
        
        # 增强学习强度
        learning_boost = recency_factor * 0.1
        self.training.learning_strength = min(1.0, 
            self.training.learning_strength + learning_boost
        )
        
        # 更新梯度信号
        self.training.gradient_signal = (
            self.training.learning_strength * 
            self.training.activation_weight *
            recency_factor
        )
        
        # 记录激活历史
        self.training.last_activated = now
        self.training.training_count += 1
        self.training.activation_history.append({
            "type": activation_type.value,
            "timestamp": now,
            "weight": self.training.activation_weight,
            "strength": self.training.learning_strength,
        })
        
        # 保留最近20条历史
        if len(self.training.activation_history) > 20:
            self.training.activation_history = self.training.activation_history[-20:]
        
        return self.training.gradient_signal
    
    def decay(self, factor: float = 0.02) -> float:
        """衰减记忆，降低激活权重
        
        Returns:
            衰减后的梯度信号
        """
        self.training.activation_weight = max(0.1, 
            self.training.activation_weight * (1 - factor)
        )
        self.training.decay_rate *= (1 - factor * 0.1)
        
        # 降低学习强度
        self.training.learning_strength = max(0.0,
            self.training.learning_strength * self.training.decay_rate
        )
        
        self.training.last_modified = time.time()
        self.training.gradient_signal = (
            self.training.learning_strength * 
            self.training.activation_weight
        )
        
        return self.training.gradient_signal
    
    def add_function_tag(self, tag: str) -> None:
        """添加函数标签
        
        函数标签是锚点，不参与记忆内容本身
        只用于训练算法进行记忆优化的参数标记
        """
        if tag not in self.training.function_tags:
            self.training.function_tags.append(tag)
    
    def remove_function_tag(self, tag: str) -> None:
        """移除函数标签"""
        if tag in self.training.function_tags:
            self.training.function_tags.remove(tag)
    
    def get_priority_score(self) -> float:
        """获取优先级评分
        
        综合学习强度、激活权重、时间衰减计算优先级
        用于策略性记忆加载
        """
        now = time.time()
        time_since_created = now - self.training.created_at
        time_since_activated = now - self.training.last_activated
        
        # 时间因子 (新记忆和近期激活的优先)
        age_factor = 1.0 / (1.0 + time_since_created / 3600)  # 小时级
        recency_factor = 1.0 / (1.0 + time_since_activated / 300)  # 分钟级
        
        # 综合评分
        score = (
            self.training.learning_strength * 0.3 +
            self.training.activation_weight * 0.3 +
            self.importance * 0.2 +
            age_factor * 0.1 +
            recency_factor * 0.1
        )
        
        return min(1.0, score)
    
    def should_promote_to_long_term(self, min_strength: float = 0.6, 
                                     min_training_count: int = 5) -> bool:
        """判断是否应该晋升到长期记忆
        
        条件:
        1. 学习强度达标
        2. 训练次数达标
        3. 激活权重保持
        """
        return (
            self.training.learning_strength >= min_strength and
            self.training.training_count >= min_training_count and
            self.training.activation_weight >= 0.4
        )
    
    def get_training_anchors(self) -> dict:
        """获取训练锚点
        
        返回用于训练算法的锚点参数
        不包含记忆内容本身
        """
        return {
            "entry_id": self.entry_id,
            "learning_strength": self.training.learning_strength,
            "activation_weight": self.training.activation_weight,
            "gradient_signal": self.training.gradient_signal,
            "training_count": self.training.training_count,
            "decay_rate": self.training.decay_rate,
            "function_tags": self.training.function_tags,
            "created_at": self.training.created_at,
            "last_activated": self.training.last_activated,
            "priority_score": self.get_priority_score(),
        }


class MemoryExpert:
    """记忆专家 - 可持续训练的记忆算法
    
    核心能力:
    1. 策略性记忆加载 - 按学习强度和激活权重从短期池加载
    2. 训练锚点 - 提供给外部训练算法使用的参数
    3. 记忆优化 - 基于梯度的遗忘和巩固
    """
    
    def __init__(self, capacity: int = 100) -> None:
        self._capacity = capacity
        self._entries: dict[str, MemoryExpertEntry] = {}
        self._short_term_pool: list[str] = []  # 短期记忆池ID列表
        
    def add(self, entry: MemoryExpertEntry) -> None:
        """添加记忆条目"""
        # 容量控制
        if len(self._entries) >= self._capacity:
            self._evict_lowest_priority()
        
        self._entries[entry.entry_id] = entry
        
        if entry.stage == MemoryStage.SHORT_TERM:
            self._short_term_pool.append(entry.entry_id)
    
    def activate(self, entry_id: str, 
                 activation_type: ActivationType = ActivationType.RECALL
                 ) -> float | None:
        """激活记忆条目
        
        Returns:
            激活强度，条目不存在返回None
        """
        entry = self._entries.get(entry_id)
        if not entry:
            return None
        
        signal = entry.activate(activation_type)
        
        # 更新短期池中的位置
        if entry_id in self._short_term_pool:
            self._reorder_short_term(entry_id, entry.get_priority_score())
        
        return signal
    
    def load_from_short_term(self, limit: int = 5, 
                            min_priority: float = 0.3) -> list[MemoryExpertEntry]:
        """从短期记忆池策略性加载
        
        按优先级评分从高到低加载
        只返回达到最低优先级的条目
        """
        # 按优先级排序。
        # 原实现 `key=lambda eid: self._entries.get(eid, MemoryExpertEntry("", "", None)).get_priority_score()`
        # 有两个问题：① 每次比较都要构造一个临时 MemoryExpertEntry（O(n log n) 次分配）；
        # ② 用位置参数传必填字段，字段顺序一变就静默错位。
        # 改为先取一次分数、跳过缺失项。
        def _score(eid: str) -> float:
            entry = self._entries.get(eid)
            return entry.get_priority_score() if entry is not None else -1.0

        sorted_pool = sorted(
            self._short_term_pool,
            key=_score,
            reverse=True,
        )
        
        loaded = []
        for entry_id in sorted_pool[:limit * 2]:  # 多取一些备选
            entry = self._entries.get(entry_id)
            if entry and entry.get_priority_score() >= min_priority:
                # 自动激活关联
                self.activate(entry_id, ActivationType.ASSOCIATE)
                loaded.append(entry)
                
                if len(loaded) >= limit:
                    break
        
        return loaded
    
    def get_training_anchors(self, limit: int = 10) -> list[dict]:
        """获取训练锚点列表
        
        用于外部训练算法进行记忆优化
        """
        # 按梯度信号排序
        sorted_entries = sorted(
            self._entries.values(),
            key=lambda e: e.training.gradient_signal,
            reverse=True
        )
        
        return [e.get_training_anchors() for e in sorted_entries[:limit]]
    
    def optimize(self) -> dict:
        """记忆优化 - 衰减和巩固
        
        1. 衰减低优先级记忆
        2. 晋升达标短期记忆
        3. 修剪过低优先级的
        """
        decayed = []
        promoted = []
        pruned = []
        
        for entry in list(self._entries.values()):
            # 衰减
            if entry.training.activation_weight < 0.3:
                entry.decay(0.05)
                decayed.append(entry.entry_id)
            
            # 晋升检查
            if entry.stage == MemoryStage.SHORT_TERM:
                if entry.should_promote_to_long_term():
                    entry.stage = MemoryStage.LONG_TERM
                    promoted.append(entry.entry_id)
                    if entry.entry_id in self._short_term_pool:
                        self._short_term_pool.remove(entry.entry_id)
            
            # 修剪检查
            if entry.get_priority_score() < 0.1:
                del self._entries[entry.entry_id]
                pruned.append(entry.entry_id)
                if entry.entry_id in self._short_term_pool:
                    self._short_term_pool.remove(entry.entry_id)
        
        return {
            "decayed": len(decayed),
            "promoted": len(promoted),
            "pruned": len(pruned),
            "total_entries": len(self._entries),
            "short_term_pool_size": len(self._short_term_pool),
        }
    
    def get(self, entry_id: str) -> MemoryExpertEntry | None:
        return self._entries.get(entry_id)
    
    def _evict_lowest_priority(self) -> None:
        """移除最低优先级的条目"""
        if not self._entries:
            return
        
        lowest = min(
            self._entries.values(),
            key=lambda e: e.get_priority_score()
        )
        
        del self._entries[lowest.entry_id]
        if lowest.entry_id in self._short_term_pool:
            self._short_term_pool.remove(lowest.entry_id)
    
    def _reorder_short_term(self, entry_id: str, new_priority: float) -> None:
        """重新排序短期池"""
        if entry_id not in self._short_term_pool:
            return
        
        self._short_term_pool.remove(entry_id)
        
        # 插入到正确位置
        inserted = False
        for i, eid in enumerate(self._short_term_pool):
            entry = self._entries.get(eid)
            if entry and entry.get_priority_score() < new_priority:
                self._short_term_pool.insert(i, entry_id)
                inserted = True
                break
        
        if not inserted:
            self._short_term_pool.append(entry_id)
    
    @property
    def count(self) -> int:
        return len(self._entries)
    
    @property
    def short_term_count(self) -> int:
        return len(self._short_term_pool)
