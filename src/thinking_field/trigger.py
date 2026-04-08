"""触发引擎 - 判断是否触发请求，生成请求数据

借鉴 claude-code-haha 设计模式:
- Task.ts: 状态流转保护 (防死循环 = 终态保护)
- QueryEngine.ts: 预算/次数限制
"""

from __future__ import annotations
from dataclasses import dataclass, field
import time

from ..config import TriggerConfig
from ..utils.logger import logger


@dataclass(frozen=True)
class TriggerRequest:
    """触发请求数据 - 发送给大模型的请求"""
    chain_id: str
    theme: str
    content: str
    activation_level: float
    prompt: str               # 构建好的完整 prompt
    context: dict             # 附加上下文


class TriggerEngine:
    """触发引擎 - 类生物神经元阈值触发

    借鉴 claude-code-haha:
    - Task.ts 的终态保护 (isTerminalTaskStatus) → 防止重复触发
    - QueryEngine.ts 的 maxTurns/maxBudget → maxConsecutive/cooldown
    """

    def __init__(self, config: TriggerConfig | None = None) -> None:
        self.config = config or TriggerConfig()
        self._last_trigger_time: float = 0.0
        self._consecutive_count: int = 0
        self._last_triggered_chain_id: str = ""

    # ------ 核心判定 ------

    def should_trigger(
        self,
        association_score: float,
        chain_id: str,
    ) -> bool:
        """判断是否应该触发

        三重保护:
        1. 冷却期检查
        2. 连续次数检查
        3. 内容去重
        """
        # 冷却期
        if not self._check_cooldown():
            return False

        # 连续次数限制
        if not self._check_consecutive_limit():
            return False

        # 内容去重: 不是上次触发的链
        if chain_id == self._last_triggered_chain_id:
            return False

        return True

    def record_trigger(self, chain_id: str) -> None:
        """记录一次触发"""
        self._last_trigger_time = time.time()
        self._consecutive_count += 1
        self._last_triggered_chain_id = chain_id
        logger.debug(
            f"触发记录: chain={chain_id}, "
            f"连续={self._consecutive_count}, "
            f"冷却={self.config.cooldown_seconds}s"
        )

    # ------ 请求构建 ------

    def build_request(
        self,
        chain_id: str,
        theme: str,
        content: str,
        activation_level: float,
        related_chains: list[dict] | None = None,
        memory_context: list[dict] | None = None,
        last_decision: str | None = None,
    ) -> TriggerRequest:
        """构建发送给大模型的标准请求

        借鉴 claude-code-haha QueryEngine.ts 的 prompt 组装方式:
        - 当前思维状态
        - 关联分析
        - 历史记忆参考
        - 上次决策结果
        - 请执行
        """
        parts: list[str] = []

        parts.append("## 当前思维状态")
        parts.append(f"主题: {theme}")
        parts.append(f"内容: {content}")
        parts.append(f"激活强度: {activation_level:.2f}")

        if related_chains:
            parts.append("\n## 关联分析")
            for i, rc in enumerate(related_chains[:5], 1):
                parts.append(
                    f"{i}. [{rc.get('score', 0):.2f}] "
                    f"{rc.get('theme', '?')}: {rc.get('content', '')[:100]}"
                )

        if memory_context:
            parts.append("\n## 历史记忆参考")
            for i, mc in enumerate(memory_context[:5], 1):
                parts.append(f"{i}. {mc.get('data', '')[:100]}")

        if last_decision:
            parts.append("\n## 上次决策结果")
            parts.append(last_decision)

        parts.append("\n## 请执行")
        parts.append(
            "根据当前思维状态和关联分析，给出思考和决策。"
            "如果有关联思维链被激活，说明它们之间的关系并给出下一步建议。"
        )

        prompt = "\n\n".join(parts)

        return TriggerRequest(
            chain_id=chain_id,
            theme=theme,
            content=content,
            activation_level=activation_level,
            prompt=prompt,
            context={
                "related_chains": related_chains or [],
                "memory_context": memory_context or [],
                "last_decision": last_decision,
            },
        )

    # ------ 内部保护 ------

    def _check_cooldown(self) -> bool:
        """检查冷却期"""
        if self._last_trigger_time == 0.0:
            return True  # 首次触发，允许
        now = time.time()
        elapsed = now - self._last_trigger_time
        return elapsed >= self.config.cooldown_seconds

    def _check_consecutive_limit(self) -> bool:
        """检查连续触发次数"""
        if self._consecutive_count >= self.config.max_consecutive:
            # 在重置窗口内超限
            if self._last_trigger_time > 0:
                window_elapsed = time.time() - self._last_trigger_time
                if window_elapsed < self.config.reset_window:
                    logger.warning(
                        f"连续触发超限: {self._consecutive_count}/{self.config.max_consecutive}, "
                        f"冷却重置"
                    )
                    return False
            # 超出窗口，重置计数
        return True

    def reset_consecutive(self) -> None:
        """重置连续触发计数"""
        self._consecutive_count = 0
        logger.debug("连续触发计数已重置")

    @property
    def is_in_cooldown(self) -> bool:
        """是否在冷却中"""
        return not self._check_cooldown()

    @property
    def consecutive_count(self) -> int:
        return self._consecutive_count
