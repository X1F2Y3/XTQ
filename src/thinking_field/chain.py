"""思维链引擎 - 管理思维链的创建、检索、生命周期

借鉴 claude-code-haha 设计模式:
- Task.ts: 状态机 (pending→running→terminal)
- companion.ts: 确定性 ID 生成
"""

from __future__ import annotations
from dataclasses import dataclass, field
import time
import string
import random
from typing import Optional

from ..utils.logger import logger


PREFIX_CHAIN = "tc"


def _generate_chain_id() -> str:
    """生成带前缀的确定性 ID"""
    chars = string.ascii_lowercase + string.digits
    suffix = ''.join(random.choices(chars, k=8))
    return f"{PREFIX_CHAIN}_{suffix}"


@dataclass
class ThoughtChainItem:
    """单条思维链

    借鉴 Task.ts:
    - chain_id: 确定性标识 (类似 Task.id + prefix)
    - status: 状态机 (active/decayed/dormant)
    - created_at / last_activated: 时间追踪
    - activation_count: 历史激活次数
    """
    chain_id: str = field(default_factory=_generate_chain_id)
    theme: str = ""                    # 思维主题
    content: str = ""                  # 思维内容
    activation_level: float = 0.0      # 激活强度 0.0-1.0
    tags: list[str] = field(default_factory=list)
    status: str = "active"             # active | decayed | dormant
    created_at: float = field(default_factory=time.time)
    last_activated: float = 0.0
    activation_count: int = 0

    def activate(self) -> None:
        """激活思维链 - 提升强度, 类似 Task 进入 running"""
        self.activation_level = min(1.0, self.activation_level + 0.3)
        self.last_activated = time.time()
        self.activation_count += 1
        if self.status in ("dormant", "decayed"):
            self.status = "active"
        logger.debug(f"思维链 {self.chain_id} 激活: level={self.activation_level:.2f}, count={self.activation_count}")

    def decay(self, factor: float = 0.05) -> None:
        """衰减 - 未被激活的思维链自然衰退"""
        self.activation_level = max(0.0, self.activation_level - factor)
        if self.activation_level <= 0.05:
            self.status = "dormant"
        elif self.activation_level <= 0.3:
            self.status = "decayed"

    @property
    def age_seconds(self) -> float:
        """存在时长(秒)"""
        return time.time() - self.created_at

    @property
    def seconds_since_activation(self) -> float:
        """距今上次激活时间(秒)"""
        if self.last_activated <= 0:
            return float('inf')
        return time.time() - self.last_activated

    def to_dict(self) -> dict:
        """序列化 - 用于存储"""
        return {
            "chain_id": self.chain_id,
            "theme": self.theme,
            "content": self.content,
            "activation_level": self.activation_level,
            "tags": self.tags,
            "status": self.status,
            "created_at": self.created_at,
            "last_activated": self.last_activated,
            "activation_count": self.activation_count,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ThoughtChainItem":
        """反序列化 - 用于加载"""
        item = cls()
        for key in cls.__dataclass_fields__:
            setattr(item, key, data.get(key, getattr(item, key)))
        return item


class ChainManager:
    """思维链管理器

    借鉴 Task.ts 的 TaskStateBase + Task 组合模式:
    - 集中管理所有思维链
    - 按状态过滤
    - 生命周期管理
    """

    def __init__(self) -> None:
        self._chains: dict[str, ThoughtChainItem] = {}

    def add(self, chain: ThoughtChainItem) -> str:
        """添加思维链"""
        self._chains[chain.chain_id] = chain
        logger.info(f"添加思维链: {chain.chain_id} theme={chain.theme}")
        return chain.chain_id

    def create_and_add(
        self,
        theme: str,
        content: str,
        tags: list[str] | None = None,
    ) -> ThoughtChainItem:
        """创建并添加思维链"""
        chain = ThoughtChainItem(
            theme=theme,
            content=content,
            tags=tags or [],
        )
        self.add(chain)
        return chain

    def get(self, chain_id: str) -> Optional[ThoughtChainItem]:
        """获取思维链"""
        return self._chains.get(chain_id)

    def remove(self, chain_id: str) -> bool:
        """移除思维链"""
        if chain_id in self._chains:
            del self._chains[chain_id]
            logger.info(f"移除思维链: {chain_id}")
            return True
        return False

    def get_active(self) -> list[ThoughtChainItem]:
        """获取所有活跃的思维链"""
        return [
            c for c in self._chains.values()
            if c.status == "active"
        ]

    def get_above_threshold(self, threshold: float) -> list[ThoughtChainItem]:
        """获取关联强度超过阈值的思维链"""
        return [
            c for c in self._chains.values()
            if c.activation_level >= threshold
        ]

    def get_sorted_by_activation(self) -> list[ThoughtChainItem]:
        """按激活强度从高到低排序"""
        return sorted(
            self._chains.values(),
            key=lambda c: c.activation_level,
            reverse=True,
        )

    def decay_all(self, factor: float = 0.05) -> None:
        """对所有思维链进行衰减"""
        for chain in self._chains.values():
            chain.decay(factor)

    def remove_dormant_above_age(self, max_age: float = 600.0) -> list[str]:
        """移除超过指定时长的休眠链"""
        to_remove = [
            cid for cid, c in self._chains.items()
            if c.status == "dormant" and c.age_seconds > max_age
        ]
        for cid in to_remove:
            self.remove(cid)
        return to_remove

    @property
    def all_chains(self) -> list[ThoughtChainItem]:
        return list(self._chains.values())

    @property
    def count(self) -> int:
        return len(self._chains)
