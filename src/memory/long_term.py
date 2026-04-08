"""伪永久记忆层 - 维持状态机思维自维持的核心记忆

借鉴人类大脑记忆处理机制:
- 睡眠巩固 (Sleep Consolidation): 空闲期压缩/强化记忆
- 遗忘曲线 (Ebbinghaus): 无强化记忆指数衰减
- 突触修剪 (Synaptic Pruning): 关联断裂的记忆被清除
- 情绪显著性 (Emotional Salience): 高频使用+高关联度=增强
- 线索依赖提取 (Cue-Dependent Retrieval): 按场景策略载入

核心目的: 不是"永久存储"，而是维持状态机思维自维续
"""

from __future__ import annotations
from dataclasses import dataclass, field
import json
import os
import math
import time
from pathlib import Path

from .models import MemoryEntry
from ..utils.logger import logger


@dataclass
class ConsolidationConfig:
    """记忆巩固配置 - 借鉴大脑睡眠巩固机制"""
    # Ebbinghaus 遗忘曲线半衰期(秒)
    ebbinghaus_half_life: float = 3600.0          # 1小时基础半衰期
    # 显著性增强因子 (access_count 的权重)
    salience_factor: float = 0.15                  # 每次访问增加的记忆强度
    # 关联断裂阈值 (多久未被关联视为断裂)
    association_break_threshold: float = 7200.0    # 2小时未关联=断裂
    # 巩固触发间隔 (多久执行一次巩固)
    consolidation_interval: float = 300.0          # 5分钟
    # 最低保留强度 (低于此值被修剪)
    minimum_retention_threshold: float = 0.05
    # 状态机核心记忆最低强度 (核心记忆不轻易衰减到0)
    core_memory_min_strength: float = 0.3


class PseudoPermanentMemory:
    """伪永久记忆层 - 维持状态机自维续

    区别于"永久存储":
    - 有条件保留: 关联度+活跃度+显著性
    - 主动遗忘: Ebbinghaus 衰减 + 突触修剪
    - 巩固强化: 周期性压缩, 类似大脑睡眠
    - 线索提取: 按需策略载入, 不全部加载
    """

    def __init__(
        self,
        consolidation: ConsolidationConfig | None = None,
        storage_path: str | None = None,
    ) -> None:
        self.config = consolidation or ConsolidationConfig()
        self._storage_path = storage_path or str(
            Path(__file__).resolve().parents[1] / "memory_data" / "pseudo_permanent.json"
        )
        self._entries: dict[str, MemoryEntry] = {}
        self._last_consolidation: float = 0.0
        self._load()

    def add(self, entry: MemoryEntry) -> None:
        """从短期记忆晋升到伪永久记忆"""
        self._entries[entry.entry_id] = entry
        self._persist()
        logger.info(
            f"伪永久记忆添加: {entry.entry_id} "
            f"access={entry.access_count}, strength={entry.strength:.2f}"
        )

    def get(self, entry_id: str) -> MemoryEntry | None:
        return self._entries.get(entry_id)

    def access(self, entry_id: str) -> None:
        """访问记忆 - 触发显著性增强"""
        entry = self._entries.get(entry_id)
        if entry:
            entry.access()
            # 显著性增强: 每次访问提升强度
            entry.strength = min(
                1.0,
                entry.strength + self.config.salience_factor
            )
            self._persist()

    def decay_all(self) -> list[MemoryEntry]:
        """衰减所有条目 - 基于 Ebbinghaus 遗忘曲线

        返回需要突触修剪的条目
        """
        now = time.time()
        to_prune: list[MemoryEntry] = []

        for entry in self._entries.values():
            # Ebbinghaus 衰减: strength × exp(-ln(2) × age / half_life)
            elapsed = now - entry.accessed_at
            ebbinghaus_decay = math.exp(
                -math.log(2) * elapsed / self.config.ebbinghaus_half_life
            )
            entry.strength *= ebbinghaus_decay

            # 突触修剪检测: 长时间未被访问且关联断裂
            if entry.accessed_at > 0:
                time_since_access = now - entry.accessed_at
                if time_since_access > self.config.association_break_threshold:
                    entry.strength *= 0.5  # 关联断裂, 强度减半

            # 突触修剪: 低于阈值被清除
            if entry.strength < self.config.minimum_retention_threshold:
                to_prune.append(entry)

        for e in to_prune:
            del self._entries[e.entry_id]

        if to_prune:
            logger.debug(f"突触修剪: {len(to_prune)} 条, 关联断裂或强度过低")
            self._persist()

        return to_prune

    def consolidate(self, force: bool = False) -> dict:
        """记忆巩固 - 借鉴大脑睡眠巩固机制

        当记忆场空闲/低活跃时触发:
        1. 高显著性记忆增强
        2. 低显著性记忆衰减
        3. 关联断裂记忆清理
        4. 核心记忆保护
        """
        now = time.time()
        if not force and (now - self._last_consolidation) < self.config.consolidation_interval:
            return {"status": "too_soon", "elapsed": now - self._last_consolidation}

        self._last_consolidation = now
        stats = {"enhanced": 0, "decayed": 0, "pruned": 0, "core_protected": 0}

        for entry in list(self._entries.values()):
            # 高显著性: access_count >= 5 且 strength >= 0.5
            if entry.access_count >= 5 and entry.strength >= 0.5:
                entry.strength = min(1.0, entry.strength + 0.1)
                stats["enhanced"] += 1

            # 低显著性: 长期未访问
            elif now - entry.accessed_at > self.config.association_break_threshold:
                # 检查是否是核心记忆 (access_count 高但近期未激活)
                core_access_threshold = 10
                if entry.access_count >= core_access_threshold:
                    entry.strength = max(
                        entry.strength,
                        self.config.core_memory_min_strength,
                    )
                    stats["core_protected"] += 1

            # 正常衰减
            else:
                entry.strength *= 0.9
                stats["decayed"] += 1

        # 突触修剪
        pruned = self.decay_all()
        stats["pruned"] = len(pruned)

        self._persist()
        logger.info(
            f"记忆巩固完成: enhanced={stats['enhanced']}, "
            f"decayed={stats['decayed']}, pruned={stats['pruned']}, "
            f"core_protected={stats['core_protected']}"
        )
        return stats

    def get_relevant_by_context(
        self,
        tags: list[str] | None = None,
        chain_id: str | None = None,
        limit: int = 5,
    ) -> list[MemoryEntry]:
        """根据场景上下文策略载入记忆

        借鉴大脑线索依赖提取:
        不是全部加载,而是根据当前场景线索提取
        """
        now = time.time()
        candidates = []

        for entry in self._entries.values():
            score = 0.0

            # 标签匹配度
            if tags and entry.tags:
                tag_overlap = len(set(tags) & set(entry.tags))
                score += tag_overlap * 0.3

            # 关联匹配
            if chain_id and entry.chain_id == chain_id:
                score += 0.5

            # 时效性加分
            elapsed = now - entry.accessed_at
            if elapsed < 60:
                score += 0.2
            elif elapsed < 300:
                score += 0.1

            # 显著性加权
            score += entry.strength * 0.4

            if score > 0:
                candidates.append((score, entry))

        candidates.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in candidates[:limit]]

    def get_state_maintenance_memory(self, limit: int = 10) -> list[MemoryEntry]:
        """获取状态机自维续需要的记忆

        这是核心方法: 返回能维持思维场自维续的记忆
        按综合评分排序: 活跃度 + 强度 + 时效性
        """
        now = time.time()
        scored = []

        for entry in self._entries.values():
            # 状态机自维续评分:
            # - 激活次数 (反映重要性)
            # - 当前强度 (反映记忆质量)
            # - 时效性 (反映相关性)
            age_factor = math.exp(-math.log(2) * (now - entry.accessed_at) / 3600)
            score = (
                entry.access_count * 0.3 +
                entry.strength * 0.4 +
                age_factor * 0.3
            )
            scored.append((score, entry))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [e for _, e in scored[:limit]]

    def get_all(self) -> list[MemoryEntry]:
        return list(self._entries.values())

    def _persist(self) -> None:
        """持久化到文件系统"""
        try:
            os.makedirs(os.path.dirname(self._storage_path), exist_ok=True)
            data = [
                {
                    "entry_id": e.entry_id,
                    "chain_id": e.chain_id,
                    "data": str(e.data),
                    "created_at": e.created_at,
                    "strength": e.strength,
                    "accessed_at": e.accessed_at,
                    "access_count": e.access_count,
                    "tags": e.tags,
                }
                for e in self._entries.values()
            ]
            with open(self._storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"记忆持久化失败: {e}")

    def _load(self) -> None:
        """从文件系统加载"""
        if not os.path.exists(self._storage_path):
            logger.info("伪永久记忆存储文件不存在, 初始化空库")
            return
        try:
            with open(self._storage_path, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
            for raw in raw_list:
                entry = MemoryEntry(
                    entry_id=raw["entry_id"],
                    chain_id=raw.get("chain_id", ""),
                    data=raw.get("data"),
                    created_at=raw.get("created_at", 0),
                    strength=raw.get("strength", 0.5),
                    accessed_at=raw.get("accessed_at", raw.get("created_at", 0)),
                    access_count=raw.get("access_count", 0),
                    tags=raw.get("tags", []),
                )
                self._entries[entry.entry_id] = entry
            logger.info(f"伪永久记忆加载: {len(self._entries)} 条")
        except Exception as e:
            logger.error(f"记忆加载失败: {e}")

    @property
    def count(self) -> int:
        return len(self._entries)

    @property
    def stats(self) -> dict:
        """获取记忆统计信息"""
        now = time.time()
        if not self._entries:
            return {
                "total": 0,
                "high_salience": 0,
                "low_salience": 0,
                "association_broken": 0,
                "core_memories": 0,
            }

        high_salience = sum(
            1 for e in self._entries.values()
            if e.access_count >= 5 and e.strength >= 0.5
        )
        association_broken = sum(
            1 for e in self._entries.values()
            if now - e.accessed_at > self.config.association_break_threshold
        )

        return {
            "total": len(self._entries),
            "high_salience": high_salience,
            "low_salience": len(self._entries) - high_salience,
            "association_broken": association_broken,
            "core_memories": sum(
                1 for e in self._entries.values()
                if e.access_count >= 10
            ),
        }
