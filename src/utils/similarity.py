"""文本相似度计算 - V3 替换点（升级为向量相似度）"""

from __future__ import annotations
import re
from collections import Counter


def tokenize(text: str) -> list[str]:
    """分词：按中文字符 + 英文字母/数字切分"""
    # 中文单字 + 英文单词 + 数字
    tokens = re.findall(r'[\u4e00-\u9fff]|\w+', text.lower())
    return tokens


def jaccard_similarity(text_a: str, text_b: str) -> float:
    """Jaccard 文本相似度：交集 / 并集"""
    set_a = set(tokenize(text_a))
    set_b = set(tokenize(text_b))

    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0

    intersection = set_a & set_b
    union = set_a | set_b
    return len(intersection) / len(union)


def cosine_similarity(text_a: str, text_b: str) -> float:
    """基于词频的余弦相似度（轻量版，不依赖外部库）"""
    counter_a = Counter(tokenize(text_a))
    counter_b = Counter(tokenize(text_b))

    all_tokens = set(counter_a.keys()) | set(counter_b.keys())
    if not all_tokens:
        return 1.0

    dot_product = sum(
        counter_a.get(t, 0) * counter_b.get(t, 0) for t in all_tokens
    )
    mag_a = sum(v ** 2 for v in counter_a.values()) ** 0.5
    mag_b = sum(v ** 2 for v in counter_b.values()) ** 0.5

    if mag_a == 0 or mag_b == 0:
        return 0.0

    return dot_product / (mag_a * mag_b)


def tag_overlap_score(tags_a: list[str], tags_b: list[str]) -> float:
    """标签重叠度：共享标签数 / 最大标签数"""
    set_a = set(tags_a)
    set_b = set(tags_b)

    if not set_a and not set_b:
        return 0.0
    if not set_a or not set_b:
        return 0.0

    return len(set_a & set_b) / max(len(set_a), len(set_b))
