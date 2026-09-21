"""关联计算引擎 - 计算思维链之间的关联强度

借鉴 claude-code-haha 设计模式:
- QueryEngine.ts: 多维度权重加权计算 (类似语义+时序+标签)
- Tool.ts: 抽象接口 (V1 实现文本相似度, V3 可替换为向量)

关联强度 = 语义 × 0.5 + 时序 × 0.3 + 标签 × 0.2
"""

from __future__ import annotations
from dataclasses import dataclass, field
import time

from ..utils.similarity import jaccard_similarity, cosine_similarity, tag_overlap_score
from ..utils.timer import exponential_decay, linear_decay
from ..utils.logger import logger
from .chain import ThoughtChainItem, ChainManager


@dataclass
class AssociationWeights:
    """关联计算权重"""
    semantic: float = 0.5     # 语义内容权重
    temporal: float = 0.3     # 时序距离权重
    tag: float = 0.2          # 标签重叠权重

    def __post_init__(self) -> None:
        total = self.semantic + self.temporal + self.tag
        if total > 0:
            self.semantic /= total
            self.temporal /= total
            self.tag /= total


@dataclass
class AssociationResult:
    """单次关联计算结果"""
    chain_a_id: str
    chain_b_id: str
    total_score: float        # 总关联强度 0.0-1.0
    semantic_score: float     # 语义得分
    temporal_score: float     # 时序得分
    tag_score: float          # 标签得分


class AssociationEngine:
    """关联计算引擎

    借鉴 claude-code-haha QueryEngine.ts 的多维度加权计算:
    - 多个维度独立计算，加权汇总
    - 配置化权重，可随时调优
    """

    def __init__(self, weights: AssociationWeights | None = None) -> None:
        self.weights = weights or AssociationWeights()

    def compute(
        self,
        chain_a: ThoughtChainItem,
        chain_b: ThoughtChainItem,
        temporal_half_life: float = 120.0,
    ) -> AssociationResult:
        """计算两个思维链之间的关联强度 - 支持动态增强"""
        semantic = self._compute_semantic(chain_a, chain_b)
        temporal = self._compute_temporal(chain_a, chain_b, temporal_half_life)
        tag = self._compute_tag_overlap(chain_a, chain_b)

        # 动态增强：两个链都被激活过，增加关联强度
        activation_boost = 0.0
        if chain_a.activation_count > 0 and chain_b.activation_count > 0:
            # 激活次数越多，关联越强
            min_activations = min(chain_a.activation_count, chain_b.activation_count)
            activation_boost = min(0.3, min_activations * 0.05)  # 最多增加0.3

        w = self.weights
        total = (
            w.semantic * semantic +
            w.temporal * temporal +
            w.tag * tag +
            activation_boost  # 加入动态增强
        )
        total = min(1.0, total)  # 不超过1.0

        return AssociationResult(
            chain_a_id=chain_a.chain_id,
            chain_b_id=chain_b.chain_id,
            total_score=total,
            semantic_score=semantic,
            temporal_score=temporal,
            tag_score=tag,
        )

    def compute_all(
        self,
        chain_manager: ChainManager,
        temporal_half_life: float = 120.0,
    ) -> list[AssociationResult]:
        """计算所有思维链两两之间的关联强度"""
        chains = chain_manager.get_active()
        results: list[AssociationResult] = []

        for i in range(len(chains)):
            for j in range(i + 1, len(chains)):
                result = self.compute(chains[i], chains[j], temporal_half_life)
                results.append(result)

        # 按总强度降序
        results.sort(key=lambda r: r.total_score, reverse=True)
        return results

    def _compute_semantic(
        self, a: ThoughtChainItem, b: ThoughtChainItem
    ) -> float:
        """语义相似度

        V1: 文本 Jaccard + Cosine 融合
        V3: 替换为向量余弦相似度
        """
        if not a.content or not b.content:
            return 0.0

        jaccard = jaccard_similarity(a.content, b.content)
        cosine = cosine_similarity(a.content, b.content)
        return jaccard * 0.4 + cosine * 0.6  # 更偏好余弦

    def _compute_temporal(
        self, a: ThoughtChainItem, b: ThoughtChainItem, half_life: float
    ) -> float:
        """时序关联度

        借鉴人类脑科学中的"时序邻近性":
        相邻激活的思维链自然增强关联
        """
        if a.last_activated <= 0 or b.last_activated <= 0:
            return 0.0

        distance = abs(a.last_activated - b.last_activated)
        return exponential_decay(distance, half_life)

    def _compute_tag_overlap(
        self, a: ThoughtChainItem, b: ThoughtChainItem
    ) -> float:
        """标签重叠度"""
        if not a.tags or not b.tags:
            return 0.0
        return tag_overlap_score(a.tags, b.tags)
