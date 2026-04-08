"""工作记忆 - 当前会话活跃信息

借鉴 claude-code-haha QueryEngine.ts 的消息生命周期:
- 容量控制: 超过容量清理最旧的
- 衰减: 随扫描降低强度
"""

from __future__ import annotations

from .models import MemoryEntry
from ..utils.logger import logger


class WorkingMemory:
    """工作记忆 - 容量有限, 快速衰减"""

    def __init__(self, capacity: int = 10) -> None:
        self._capacity = capacity
        self._entries: dict[str, MemoryEntry] = {}

    def add(self, entry: MemoryEntry) -> None:
        """添加到工作记忆"""
        if len(self._entries) >= self._capacity:
            self._evict_lowest()
        self._entries[entry.entry_id] = entry
        entry.access()
        logger.debug(f"工作记忆添加: {entry.entry_id} tags={entry.tags}")

    def get(self, entry_id: str) -> MemoryEntry | None:
        return self._entries.get(entry_id)

    def decay_all(self, factor: float = 0.05) -> list[MemoryEntry]:
        """衰减所有条目, 返回需要清理的"""
        to_cleanup: list[MemoryEntry] = []
        for entry in list(self._entries.values()):
            entry.decay(factor)
            if entry.strength <= 0.1:
                to_cleanup.append(entry)
        for e in to_cleanup:
            del self._entries[e.entry_id]
        return to_cleanup

    def promote_candidates(self, min_access_count: int = 3) -> list[MemoryEntry]:
        """获取晋升候选条目"""
        return [
            e for e in self._entries.values()
            if e.access_count >= min_access_count
        ]

    def to_list(self) -> list[MemoryEntry]:
        return list(self._entries.values())

    def _evict_lowest(self) -> None:
        """移除强度最低的条目"""
        if not self._entries:
            return
        lowest = min(self._entries.values(), key=lambda e: e.strength)
        del self._entries[lowest.entry_id]
        logger.debug(f"工作记忆溢出清理: {lowest.entry_id}")

    @property
    def count(self) -> int:
        return len(self._entries)
