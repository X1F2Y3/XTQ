"""时序工具 - 时间衰减函数"""

from __future__ import annotations
import time
import math


def time_distance_seconds(dt1: float, dt2: float | None = None) -> float:
    """计算两个时间戳之间的秒数差"""
    if dt2 is None:
        dt2 = time.time()
    return abs(dt2 - dt1)


def exponential_decay(distance: float, half_life: float = 60.0) -> float:
    """指数衰减函数

    距离越近越接近1.0，距离越远越接近0.0
    类似半衰期衰减
    """
    if distance <= 0:
        return 1.0
    return math.exp(-math.log(2) * distance / half_life)


def linear_decay(distance: float, max_distance: float = 300.0) -> float:
    """线性衰减函数"""
    if distance <= 0:
        return 1.0
    return max(0.0, 1.0 - distance / max_distance)


def normalize(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """将值归一化到指定范围"""
    if max_val == min_val:
        return 0.5
    return max(min_val, min(max_val, (value - min_val) / (max_val - min_val)))
