"""질문 도메인별 expert 프롬프트 선택

사용:
    from experts import get_expert, build_expert_system, EXPERT_LABELS

    expert_id = get_expert("좋아하는 사람이 날 어떻게 생각할까")  # 'love'
    system_prompt = build_expert_system(expert_id)
    label = EXPERT_LABELS[expert_id]
"""
from .router import get_expert, keyword_match
from .prompts import (
    build_expert_system,
    EXPERT_PROMPTS,
    EXPERT_IDS,
    EXPERT_LABELS,
)

__all__ = [
    'get_expert',
    'keyword_match',
    'build_expert_system',
    'EXPERT_PROMPTS',
    'EXPERT_IDS',
    'EXPERT_LABELS',
]
