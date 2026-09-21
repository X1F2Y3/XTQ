#!/usr/bin/env python3
"""思维动态场 (TDF) - 主入口

Usage:
    python src/main.py            # Mock 模式（无需 API Key，当前唯一可用模式）

说明：OpenAI / Claude 适配器尚未实现（见 README 路线图），因此不提供
--openai / --claude 参数 —— 不承诺做不到的事。
"""

from __future__ import annotations
import asyncio
import argparse
import signal
import sys

# 确保项目根目录在 path 中，使相对导入正确工作
import os as _os
_root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from src.config import TDFConfig
from src.utils.logger import setup_logger
from src.thinking_field.field import ThinkingField, FieldEvent
from src.thinking_field.chain import ThoughtChainItem

logger = setup_logger("tdf.main", "INFO")


async def main() -> None:
    parser = argparse.ArgumentParser(description="思维动态场 (TDF)")
    parser.add_argument(
        "--provider",
        choices=["mock"],
        default="mock",
        help="模型适配器（当前仅 mock 可用）",
    )
    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("思维动态场 (Thinking Dynamic Field) v0.1.0")
    logger.info("=" * 60)

    # 1. 创建思维场
    config = TDFConfig(model_provider=args.provider)
    field = ThinkingField(config)

    # 2. 初始化种子思维链（模拟用户输入/系统注入）
    logger.info("初始化种子思维链...")
    chains: list[ThoughtChainItem] = [
        field.add_chain(
            theme="探索AI架构",
            content="思考大模型的局限性和外挂架构的可行性",
            tags=["AI", "架构", "大模型"]
        ),
        field.add_chain(
            theme="AI模型思考",
            content="大模型需要自主思考能力，而不是被动响应",
            tags=["AI", "思考", "模型"]
        ),
        field.add_chain(
            theme="智能体设计",
            content="构建能主动思考和决策的智能体架构",
            tags=["智能体", "AI", "架构"]
        ),
        field.add_chain(
            theme="类脑思维场",
            content="模拟人脑的关联计算和记忆巩固机制",
            tags=["类脑", "记忆", "关联"]
        ),
        field.add_chain(
            theme="动态触发逻辑",
            content="阈值触发替代固定频率扫描，类似神经元放电",
            tags=["触发", "动态", "逻辑"]
        ),
    ]

    logger.info(f"种子思维链已添加: {[c.theme for c in chains]}")

    # 3. 启动思维场
    stop_event = asyncio.Event()

    def _handle_signal(sig: int, frame: object) -> None:
        logger.info(f"收到信号 {signal.Signals(sig).name}, 准备停止...")
        stop_event.set()

    signal.signal(signal.SIGINT, _handle_signal)
    # ★ Windows 上**没有 SIGTERM**（`signal.SIGTERM` 在 Windows Python 中不存在，
    #   直接访问会 AttributeError 让主入口一启动就崩）。用 getattr 探测后再注册。
    _sigterm = getattr(signal, "SIGTERM", None)
    if _sigterm is not None:
        signal.signal(_sigterm, _handle_signal)

    logger.info("思维场开始运行. Press Ctrl+C 停止.")

    cycle_count = 0

    async for event in field.start():
        _handle_event(event, cycle_count)
        if event.event_type == "cycle_complete":
            cycle_count += 1

        # 最多运行 10 个周期后自动停止（测试用）
        if cycle_count >= 10:
            logger.info(f"已完成 {cycle_count} 个周期, 自动停止.")
            break

        # 检查停止信号
        if stop_event.is_set():
            break

    # 4. 输出统计
    logger.info("=" * 60)
    logger.info(f"思维场关闭. 总周期数: {cycle_count}")
    stats = field.stats
    logger.info(f"最终统计:")
    logger.info(f"  思维链总数: {stats['chain_count']}")
    logger.info(f"  活跃思维链: {stats['active_chains']}")
    logger.info(f"  记忆统计: {stats['memory']}")
    logger.info("=" * 60)


def _handle_event(event: FieldEvent, cycle: int) -> None:
    """处理思维场事件"""
    if event.event_type == "field_started":
        logger.info(f"[周期 {cycle}] 思维场启动")
    elif event.event_type == "association_computed":
        score = event.data.get("total_score", 0)
        logger.info(
            f"[周期 {cycle}] 关联计算: {event.data['chain_a'][:6]} <-> "
            f"{event.data['chain_b'][:6]} score={score:.4f}"
        )
    elif event.event_type == "trigger_activated":
        logger.info(
            f"[周期 {cycle}] ** 触发激活: {event.data['theme']} "
            f"(prompt={event.data['prompt_length']} chars)"
        )
    elif event.event_type == "model_response":
        resp = event.data.get("response", "")
        # 输出响应摘要（前 100 字）
        summary = resp[:100].replace("\n", " ")
        logger.info(
            f"[周期 {cycle}] 模型响应: {summary}..."
            f" (总长度={event.data['response_length']})"
        )
    elif event.event_type == "memory_optimized":
        stats = event.data
        logger.info(
            f"[周期 {cycle}] 记忆优化: "
            f"晋升短期={stats.get('promoted_to_short', 0)}, "
            f"晋升永久={stats.get('promoted_to_permanent', 0)}, "
            f"巩固={stats.get('consolidation', {}).get('enhanced', 0)}"
        )
    elif event.event_type == "cycle_complete":
        logger.info(
            f"[周期 {cycle}] 周期完成 | "
            f"活跃链: {event.data.get('active_chains', 0)}, "
            f"记忆: {event.data.get('memory_stats', {})}"
        )
    elif event.event_type == "field_stopped":
        logger.info(f"[周期 {cycle}] 思维场停止")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("用户中断, 退出")
    except Exception as e:
        logger.error(f"运行异常: {e}", exc_info=True)
        sys.exit(1)
