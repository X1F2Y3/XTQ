"""ThinkingField - 思维动态场主控制器

借鉴 claude-code-haha QueryEngine.ts 的设计模式:
- 异步生成器: 事件流 (yield messages like SDKMessage)
- 状态保持: 跨 turn 保持思维场状态
- 协调各模块: 关联→触发→响应→记忆优化
"""

from __future__ import annotations
import asyncio
import time
from dataclasses import dataclass
from typing import AsyncGenerator

from ..config import TDFConfig
from ..utils.logger import logger
from ..memory.models import MemoryEntry
from ..memory.system import MemorySystem
from .chain import ThoughtChainItem, ChainManager
from .association import AssociationEngine, AssociationResult
from .trigger import TriggerEngine, TriggerRequest
from ..adapter.mock import MockAdapter, BaseAdapter


@dataclass
class FieldEvent:
    """思维场事件 - 类似 claude-code-haha 的 SDKMessage"""
    event_type: str   # chain_added | association_computed | trigger_activated |
                      # model_response | memory_optimized | cycle_complete
    data: dict
    timestamp: float = 0.0

    def __post_init__(self) -> None:
        if self.timestamp == 0.0:
            self.timestamp = time.time()


class ThinkingField:
    """思维动态场 - 主控制器

    核心职责:
    1. 维护思维链状态 (ChainManager)
    2. 计算关联强度 (AssociationEngine)
    3. 判断触发条件 (TriggerEngine)
    4. 调用大模型 (ModelAdapter - Mock for now)
    5. 管理记忆流转 (MemorySystem)
    6. 优化记忆 (优化/巩固/沉淀)
    """

    def __init__(self, config: TDFConfig | None = None) -> None:
        self.config = config or TDFConfig()
        self.chain_manager = ChainManager()
        self.association_engine = AssociationEngine()
        self.trigger_engine = TriggerEngine()
        self.memory_system = MemorySystem()
        self.model_adapter: BaseAdapter = MockAdapter()
        self._running = False
        self._last_decision: str | None = None

    # ------ 公共接口 ------

    def add_chain(self, theme: str, content: str, tags: list[str] | None = None) -> ThoughtChainItem:
        """添加思维链到工作记忆"""
        chain = self.chain_manager.create_and_add(theme, content, tags=tags or [])
        # 同时添加到工作记忆
        self.memory_system.add_to_working(MemoryEntry(
            chain_id=chain.chain_id,
            data=content,
            tags=tags or [],
            strength=0.8,
        ))
        return chain

    def remove_chain(self, chain_id: str) -> bool:
        """移除思维链"""
        return self.chain_manager.remove(chain_id)

    async def start(self) -> AsyncGenerator[FieldEvent, None]:
        """启动思维场扫描循环

        借鉴 QueryEngine.submitMessage() 的异步生成器模式:
        调用方可以通过 async for 接收每个阶段的事件
        """
        self._running = True
        logger.info(
            f"思维场启动: interval={self.config.field_config.scan_interval}s, "
            f"threshold={self.config.field_config.activation_threshold}"
        )
        yield FieldEvent("field_started", {"status": "running"})

        try:
            while self._running:
                async for event in self._run_cycle():
                    yield event
                await asyncio.sleep(self.config.field_config.scan_interval)
        finally:
            self._running = False
            logger.info("思维场停止")

    def get_active_chains(self) -> list[ThoughtChainItem]:
        """获取所有活跃思维链"""
        return self.chain_manager.get_active()

    # ------ 核心循环 ------

    async def _run_cycle(self) -> AsyncGenerator[FieldEvent, None]:
        """运行完整的思维场扫描周期"""
        # 1. 关联计算
        associations = self.association_engine.compute_all(self.chain_manager)
        for assoc in associations:
            yield FieldEvent("association_computed", {
                "chain_a": assoc.chain_a_id,
                "chain_b": assoc.chain_b_id,
                "total_score": assoc.total_score,
            })

        # 2. 检测触发
        high_score = associations[0] if associations else None
        
        if high_score and high_score.total_score >= self.config.field_config.activation_threshold:
            # 触发前检查 (防死循环)
            chain = self.chain_manager.get(high_score.chain_a_id)
            if chain and self.trigger_engine.should_trigger(
                high_score.total_score, high_score.chain_a_id
            ):
                async for event in self._do_trigger(chain, associations):
                    yield event
        else:
            # 无触发 → 衰减低关联链
            self.chain_manager.decay_all(self.config.trigger.decay_factor)

        # 3. 记忆优化
        self.trigger_engine.reset_consecutive()
        opt_result = self.memory_system.optimize()
        yield FieldEvent("memory_optimized", opt_result)

        # 4. 清理休眠链
        cleaned = self.chain_manager.remove_dormant_above_age()
        if cleaned:
            logger.debug(f"清理休眠链: {len(cleaned)} 条")

        # 5. 周期完成
        yield FieldEvent("cycle_complete", {
            "active_chains": self.chain_manager.count,
            "memory_stats": self.memory_system.stats,
        })

    async def _do_trigger(
        self,
        chain: ThoughtChainItem,
        associations: list[AssociationResult],
    ) -> AsyncGenerator[FieldEvent, None]:
        """执行触发 - 调用大模型并处理响应"""

        # 1. 构建请求
        related_chains = [
            {
                "chain_id": assoc.chain_b_id,
                "score": assoc.total_score,
                "theme": self.chain_manager.get(assoc.chain_b_id).theme
                if self.chain_manager.get(assoc.chain_b_id)
                else "?",
                "content": self.chain_manager.get(assoc.chain_b_id).content
                if self.chain_manager.get(assoc.chain_b_id)
                else "",
            }
            for assoc in associations[:3]
            if assoc.chain_b_id != chain.chain_id
        ]

        memory_context = [
            {"data": m.data, "tags": m.tags}
            for m in self.memory_system.get_relevant(chain.tags, limit=3)
        ]

        request = self.trigger_engine.build_request(
            chain_id=chain.chain_id,
            theme=chain.theme,
            content=chain.content,
            activation_level=chain.activation_level,
            related_chains=related_chains,
            memory_context=memory_context,
            last_decision=self._last_decision,
        )

        yield FieldEvent("trigger_activated", {
            "chain_id": chain.chain_id,
            "theme": chain.theme,
            "prompt_length": len(request.prompt),
        })

        # 2. 调用大模型 (非阻塞)
        self.trigger_engine.record_trigger(chain.chain_id)
        chain.activate()

        raw_response = ""
        async for token in self.model_adapter.send(request.prompt, request.context):
            raw_response += token

        # 3. 解析响应
        self._last_decision = raw_response

        yield FieldEvent("model_response", {
            "chain_id": chain.chain_id,
            "response": raw_response,
            "response_length": len(raw_response),
        })

        # 4. 更新记忆
        self.memory_system.add_to_working(MemoryEntry(
            chain_id=chain.chain_id,
            data=raw_response,
            tags=chain.tags + ["model_response"],
            strength=0.7,
        ))

    @property
    def stats(self) -> dict:
        """获取思维场完整统计"""
        return {
            "chain_count": self.chain_manager.count,
            "active_chains": len(self.chain_manager.get_active()),
            "memory": self.memory_system.stats,
            "trigger": {
                "consecutive_count": self.trigger_engine.consecutive_count,
                "in_cooldown": self.trigger_engine.is_in_cooldown,
            },
            "model_adapter": self.model_adapter.stats,
        }
