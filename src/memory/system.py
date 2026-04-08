"""记忆系统主控制器 - 协调三层记忆流转与优化

借鉴 claude-code-haha QueryEngine.ts:
- 消息流转: user→assistant→result
- 沉淀策略: 工作记忆→短期记忆→长期记忆→伪永久记忆
- 衰减清理: 类似 compact 边界清理
"""

from __future__ import annotations

from ..config import MemoryConfig
from ..utils.logger import logger
from .models import MemoryEntry
from .working import WorkingMemory
from .short_term import ShortTermMemory
from .long_term import PseudoPermanentMemory, ConsolidationConfig


class MemorySystem:
    """记忆系统主控制器

    管理三层记忆 + 伪永久记忆:
    - 工作记忆: 当前会话, 快速衰减
    - 短期记忆: 激活次数达标后晋升
    - 伪永久记忆: 维持状态机自维续, 有条件保留/主动遗忘/巩固强化
    """

    def __init__(
        self,
        config: MemoryConfig | None = None,
        consolidation: ConsolidationConfig | None = None,
    ) -> None:
        self.config = config or MemoryConfig()
        self.working = WorkingMemory(capacity=self.config.working_capacity)
        self.short_term = ShortTermMemory(capacity=self.config.short_capacity)
        self.pseudo_permanent = PseudoPermanentMemory(consolidation=consolidation)

    def add_to_working(self, entry: MemoryEntry) -> None:
        """添加到工作记忆"""
        self.working.add(entry)

    def promote_to_short(self, entry: MemoryEntry) -> bool:
        """从工作记忆晋升到短期记忆"""
        if entry.access_count < self.config.short_promote_count:
            return False
        self.short_term.add(entry)
        logger.info(f"记忆晋升→短期: {entry.entry_id} access={entry.access_count}")
        return True

    def promote_to_permanent(
        self, entry: MemoryEntry, avg_association: float = 0.0
    ) -> bool:
        """从短期记忆晋升到伪永久记忆"""
        if entry.access_count < self.config.long_promote_count:
            return False
        if avg_association > 0 and avg_association < self.config.long_min_association:
            return False
        self.pseudo_permanent.add(entry)
        logger.info(
            f"记忆晋升→伪永久: {entry.entry_id} "
            f"access={entry.access_count}, assoc={avg_association:.2f}"
        )
        return True

    def get_relevant(self, tags: list[str], limit: int = 5) -> list[MemoryEntry]:
        """获取相关记忆 (综合伪永久和短期)"""
        permanent_relevant = self.pseudo_permanent.get_relevant_by_context(
            tags=tags, limit=limit,
        )
        remaining = limit - len(permanent_relevant)
        if remaining > 0:
            short_relevant = self.short_term.get_relevant(tags, remaining)
            return permanent_relevant + short_relevant
        return permanent_relevant

    def optimize(self) -> dict:
        """记忆优化 - 衰减 + 沉淀 + 清除

        1. 所有记忆层衰减
        2. 工作记忆→短期记忆晋升
        3. 短期记忆→伪永久记忆晋升
        4. 伪永久记忆巩固(类似大脑睡眠巩固)
        """
        # 1. 衰减
        working_cleaned = self.working.decay_all(self.config.working_decay)
        short_cleaned = self.short_term.decay_all()
        permanent_pruned = self.pseudo_permanent.decay_all()

        if working_cleaned:
            logger.debug(f"工作记忆清理: {len(working_cleaned)} 条")
        if short_cleaned:
            logger.debug(f"短期记忆清理: {len(short_cleaned)} 条")
        if permanent_pruned:
            logger.debug(f"伪永久记忆修剪: {len(permanent_pruned)} 条")

        # 2. 工作记忆→短期记忆晋升
        working_candidates = self.working.promote_candidates(self.config.short_promote_count)
        for entry in working_candidates:
            self.promote_to_short(entry)

        # 3. 短期记忆→伪永久记忆晋升
        short_candidates = self.short_term.promote_candidates(
            self.config.long_promote_count,
            self.config.long_min_association,
        )
        for entry in short_candidates:
            self.promote_to_permanent(entry, avg_association=entry.strength)

        # 4. 伪永久记忆巩固
        consolidation_stats = self.pseudo_permanent.consolidate()

        return {
            "working_cleaned": len(working_cleaned),
            "short_cleaned": len(short_cleaned),
            "permanent_pruned": len(permanent_pruned),
            "promoted_to_short": len(working_candidates),
            "promoted_to_permanent": len(short_candidates),
            "consolidation": consolidation_stats,
        }

    @property
    def stats(self) -> dict:
        """获取记忆统计"""
        return {
            "working_count": self.working.count,
            "short_count": self.short_term.count,
            "permanent_count": self.pseudo_permanent.count,
            "permanent_detail": self.pseudo_permanent.stats,
            "total": (
                self.working.count
                + self.short_term.count
                + self.pseudo_permanent.count
            ),
        }
