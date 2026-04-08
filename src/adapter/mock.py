"""Mock 适配器 - 测试用，无需真实 API Key

借鉴 claude-code-haha QueryEngine.ts 的 query() 异步生成器模式:
- 生成器逐段 yield 响应
- 非阻塞事件流

模拟大模型的行为:
- 接收 prompt → 延迟返回 → 模拟 token 流
- 返回带标签的结构化响应
"""

from __future__ import annotations
import asyncio
import random
from typing import AsyncGenerator


class BaseAdapter:
    """大模型适配器的抽象基类

    V3 演进路线: 从 API 调用接口 → 执行器接口
    """

    async def send(self, prompt: str, context: dict | None = None) -> AsyncGenerator[str, None]:
        """发送请求，异步逐段返回响应"""
        raise NotImplementedError

    async def send_complete(self, prompt: str, context: dict | None = None) -> str:
        """发送请求，等待完整响应"""
        response_parts: list[str] = []
        async for part in self.send(prompt, context):
            response_parts.append(part)
        return "".join(response_parts)


class MockAdapter(BaseAdapter):
    """Mock 适配器 - 模拟大模型的主动响应"""

    def __init__(self, delay: float = 0.3, name: str = "mock-model") -> None:
        self._delay = delay
        self._name = name
        self._call_count = 0

    async def send(self, prompt: str, context: dict | None = None) -> AsyncGenerator[str, None]:
        """模拟大模型响应:
        - 分析 prompt 内容
        - 生成有意义的 mock 响应
        - 模拟 token 流式输出
        """
        self._call_count += 1

        # 模拟生成延迟
        await asyncio.sleep(self._delay * random.uniform(0.5, 1.5))

        # 基于 prompt 内容生成有意义的响应
        # (不是死板的模板，而是根据输入内容调整)
        response_parts = self._generate_response(prompt, context)

        # 逐段模拟流式输出
        for part in response_parts:
            await asyncio.sleep(self._delay * 0.3)
            yield part

    def _generate_response(self, prompt: str, context: dict | None) -> list[str]:
        """生成模拟响应的内容"""
        responses = []

        # 提取 prompt 关键信息
        has_current_state = "当前思维状态" in prompt
        has_association = "关联分析" in prompt
        has_memory = "历史记忆参考" in prompt
        has_decision = "上次决策结果" in prompt

        responses.append(f"[Mock: 收到请求 #{self._call_count}]\n\n")

        if has_current_state:
            # 提取主题并生成响应
            if "主题:" in prompt:
                theme_start = prompt.find("主题:")
                theme_end = prompt.find("\n", theme_start)
                theme = prompt[theme_start:theme_end].strip() if theme_end > 0 else ""
                responses.append(f"## 思维状态分析\n{theme}\n\n")

            if "激活强度:" in prompt:
                strength_start = prompt.find("激活强度:")
                strength_end = prompt.find("\n", strength_start)
                strength = prompt[strength_start:strength_end].strip() if strength_end > 0 else ""
                responses.append(f"## 激活分析\n{strength} — 达到触发阈值，思维链活跃\n\n")

        if has_association:
            responses.append("## 关联发现\n检测到多条思维链之间的语义和时序关联，建议进行交叉思考。\n\n")

        if has_memory:
            responses.append("## 记忆回顾\n历史模式显示类似关联已激活过，可作为参考。\n\n")

        if has_decision:
            responses.append("## 决策回溯\n上次决策的反馈已被吸收，正在调整方向。\n\n")

        responses.append("## 下一步建议\n基于当前激活状态，建议保持思维链的并行探索，观察关联是否进一步增强。")

        return responses

    @property
    def stats(self) -> dict:
        return {
            "name": self._name,
            "is_mock": True,
            "call_count": self._call_count,
            "response_delay": self._delay,
        }
