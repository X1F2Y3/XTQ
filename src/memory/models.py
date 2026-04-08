"""记忆数据模型 - V1/V2/V3 通用接口

借鉴 claude-code-haha Task.ts 的设计：
- 确定性ID + 前缀
- 状态流转到终端不再变
- 时间追踪字段

注意：思维链实体在 thinking_field/chain.py 的 ThoughtChainItem 中定义。
本文件只负责记忆数据模型。
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import time
import string
import random


PREFIX_MEMORY = "mem"


def _generate_memory_id() -> str:
    """生成带前缀的确定性记忆ID"""
    chars = string.ascii_lowercase + string.digits
    suffix = ''.join(random.choices(chars, k=8))
    return f"{PREFIX_MEMORY}_{suffix}"


def to_memory_expert_entry(entry: "MemoryEntry") -> "MemoryExpertEntry":
    """将 MemoryEntry 转换为 MemoryExpertEntry
    
    用于新旧记忆模型的桥接
    """
    from .memory_expert import (
        MemoryExpertEntry, MemoryStage, TrainingParams
    )
    
    return MemoryExpertEntry(
        entry_id=entry.entry_id,
        chain_id=entry.chain_id,
        data=entry.data,
        stage=MemoryStage.WORKING,
        tags=entry.tags,
        importance=entry.strength,
        training=TrainingParams(
            created_at=entry.created_at,
            last_activated=entry.accessed_at,
            last_modified=entry.accessed_at,
        ),
    )


@dataclass
class MemoryEntry:
    """记忆条目 - V1/V2/V3 兼容（V3 扩展 metadata）

    借鉴 claude-code-haha TaskStateBase:
    - entry_id: 确定性标识
    - 时间追踪: created_at / accessed_at
    - 访问计数: 类似 activation_count
    - metadata: 扩展字段（V3 使用）
    """
    entry_id: str = field(default_factory=_generate_memory_id)
    chain_id: str = ""
    data: Any = None                     # V1=str, V2=Text+Vector, V3=Weights
    created_at: float = field(default_factory=time.time)
    strength: float = 0.5
    accessed_at: float = field(default_factory=time.time)
    access_count: int = 0
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def access(self) -> None:
        """访问此记忆条目 - 更新访问时间"""
        self.access_count += 1
        self.accessed_at = time.time()

    def decay(self, factor: float = 0.02) -> None:
        """衰减 - 随时间降低强度"""
        self.strength = max(0.0, self.strength - factor)
