"""短期记忆 - 会话间保留的活跃记忆

借鉴 claude-code-haha QueryEngine.ts 的 compact 边界机制:
- 容量控制, 超量淘汰低优先级条目
- 时间衰减, 自然衰退
"""

from __future__ import annotations

from .models import MemoryEntry
from ..utils.logger import logger


class ShortTermMemory:
    """短期记忆 - 容量较大, 时间衰减"""

    def __init__(self, capacity: int = 100, cleanup_threshold: float = 0.05) -> None:
        self._capacity = capacity
        # 同 WorkingMemory：阈值必须走配置，不能写死。
        # 短期记忆比工作记忆更"耐留"，所以默认阈值更低（0.05 vs 0.1）。
        self._cleanup_threshold = cleanup_threshold
        self._entries: dict[str, MemoryEntry] = {}

    def add(self, entry: MemoryEntry) -> None:
        """从工作记忆晋升到短期记忆"""
        if entry.entry_id in self._entries:
            existing = self._entries[entry.entry_id]
            existing.strength = max(existing.strength, entry.strength)
            existing.access_count = max(existing.access_count, entry.access_count)
            return
        if len(self._entries) >= self._capacity:
            self._evict_oldest()
        self._entries[entry.entry_id] = entry
        logger.info(f"短期记忆添加: {entry.entry_id} strength={entry.strength:.2f}")

    def get(self, entry_id: str) -> MemoryEntry | None:
        return self._entries.get(entry_id)

    def decay_all(self, factor: float = 0.02) -> list[MemoryEntry]:
        """衰减所有条目, 返回需要清理的"""
        to_cleanup: list[MemoryEntry] = []
        for entry in self._entries.values():
            entry.decay(factor)
            if entry.strength <= self._cleanup_threshold:
                to_cleanup.append(entry)
        for e in to_cleanup:
            del self._entries[e.entry_id]
        return to_cleanup

    def promote_candidates(
        self,
        min_access_count: int = 2,
        min_association: float = 0.6,
    ) -> list[MemoryEntry]:
        """获取晋升到长期记忆的候选条目"""
        return [
            e for e in self._entries.values()
            if e.access_count >= min_access_count and e.strength >= min_association
        ]

    def get_relevant(self, tags: list[str], limit: int = 5) -> list[MemoryEntry]:
        """根据标签获取相关记忆"""
        if not tags:
            return []
        tag_set = set(tags)
        scored = []
        for entry in self._entries.values():
            overlap = len(tag_set & set(entry.tags))
            if overlap > 0:
                scored.append((overlap, entry))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored[:limit]]

    def access(self, entry_id: str) -> None:
        entry = self._entries.get(entry_id)
        if entry:
            entry.access()

    def to_list(self) -> list[MemoryEntry]:
        return list(self._entries.values())

    def _evict_oldest(self) -> None:
        """移除最早添加的条目"""
        if not self._entries:
            return
        oldest = min(self._entries.values(), key=lambda e: e.created_at)
        del self._entries[oldest.entry_id]
        logger.debug(f"短期记忆溢出清理: {oldest.entry_id}")

    @property
    def count(self) -> int:
        return len(self._entries)
