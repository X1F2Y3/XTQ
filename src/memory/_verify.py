"""记忆验证 - 检查记忆系统完整性"""

from __future__ import annotations

from .working import WorkingMemory
from .short_term import ShortTermMemory
from .long_term import PseudoPermanentMemory, ConsolidationConfig


class MemoryValidator:
    """记忆验证器 - 验证记忆系统是否完整可用"""

    def verify(self) -> list[str]:
        """验证记忆系统, 返回失败信息列表"""
        errors: list[str] = []

        # 验证工作记忆
        working = WorkingMemory()
        if working.count != 0:
            errors.append("工作记忆初始状态非空")

        # 验证短期记忆
        short = ShortTermMemory()
        if short.count != 0:
            errors.append("短期记忆初始状态非空")

        # 验证伪永久记忆
        permanent = PseudoPermanentMemory()
        if permanent.count != 0:
            errors.append("伪永久记忆初始状态非空")

        return errors
