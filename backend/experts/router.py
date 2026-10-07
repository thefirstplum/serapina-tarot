"""질문을 expert로 분류하는 라우터

키워드 매칭이 기본이고, 임베딩은 USE_EMBEDDING_ROUTER=true일 때만 씀.
임베딩 점수가 임계값 이상이면 키워드 결과보다 우선. 둘 다 없으면 'daily'.
"""
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# 키워드 매칭
KEYWORD_MAP = {
    'love': [
        '좋아', '짝사랑', '연애', '이별', '재회', '고백', '남친', '여친',
        '남자친구', '여자친구', '소개팅', '데이트', '결혼', '바람', '권태',
        '엄마', '아빠', '부모', '가족', '형제', '자매', '친구', '동생',
        '오빠', '언니', '누나', '형이', '형한테', '관계', '사람', '그 사람', '저 사람', '상대',
        # 구어체 표현. 이게 없을 때 "썸남한테 연락해도 될까?"가 daily로 갔다
        '썸', '썸남', '썸녀', '밀당', '애매', '연락', '카톡', '톡', '문자', 'dm',
        '읽씹', '안읽씹', '차단', '사귀', '헤어', '전남친', '전여친', '복연',
        '첫사랑', '설레', '두근', '짝남', '짝녀', '애인', '커플', '만나',
        '속마음', '진심', '마음',
        # 커뮤니티 질문 113개를 돌려 보고 추가 (2026-09-15)
        '걔', '얘', '솔탈', '솔로탈출', '모솔', '인연', '그리워', '보고싶',
        '첫인상', '잊', '미련', '호감', '썸타', '연하', '연상', '재결합',
        '사랑', '그 애', '그애', '그 남자', '그남자', '그 여자', '그여자',
    ],
    'career': [
        '회사', '직장', '일하', '일 때문', '일자리', '업무', '이직', '취업', '면접', '입사',
        '시험', '수능', '내신', '성적', '공부', '자격증',
        '퇴사', '사직', '창업', '사업', '승진', '평가', '연봉 협상',
        '진로', '커리어', '직업', '적성', '번아웃', '워라밸',
        '학교', '학과', '전공', '자퇴', '휴학', '대학원',
        '합격', '불합', '발표', '취직', '알바', '아르바이트', '스카웃',
        '스카우트', '헤드헌', '가업', '인턴', '계약직', '정규직',
    ],
    'money': [
        '돈', '재물', '재정', '투자', '주식', '코인', '비트코인', '재테크',
        '저축', '예금', '적금', '빚', '대출', '카드값', '월급', '연봉',
        '집값', '집 사', '부동산', '전세', '월세', '소비', '지출',
        '자가', '매매', '아파트', '분양', '억대', '억 대', '경제적', '경제력',
        '생활비', '재산', '상속', '등기', '청약', '보증금', '학자금',
    ],
    'self': [
        '나는', '내가', '내 인생', '나만', '자존감', '자아', '정체성',
        '의미', '가치관', '미래', '꿈', '목표', '우울', '불안', '무기력',
        '의욕', '행복', '삶', '인생', '뭘 원하는지', '왜 사는지',
        '버티', '힘들', '지쳐', '외로', '막막',
    ],
    'daily': [
        '오늘', '내일', '이번 주', '이번 달', '운세', '오늘의', '내일의',
        '주말', '여행', '시험', '약속',
    ],
}


# 한글은 어간에 받침이 붙으면 글자가 바뀐다. '사귀' + ㄹ = '사귈'이라 '사귀' in '사귈 거 같아'는 False.
# 키워드를 하나씩 더하는 대신 매칭 방식을 바꿨다.
# 한글 음절은 0xAC00 + (초성*21 + 중성)*28 + 종성 순서로 배열돼 있어서, 받침 없는 글자 X에 대해
# X..X+27이 같은 초성·중성의 받침 변형 전부다. '나'를 [나-낳]으로 바꾸면 난/날/남/났을 다 받는다.
def _kw_pattern(kw: str) -> "re.Pattern":
    last = kw[-1]
    code = ord(last)
    if 0xAC00 <= code <= 0xD7A3 and (code - 0xAC00) % 28 == 0:
        return re.compile(re.escape(kw[:-1]) + f"[{last}-{chr(code + 27)}]")
    return re.compile(re.escape(kw))


_KEYWORD_PATTERNS = {
    expert_id: [(kw, _kw_pattern(kw)) for kw in keywords]
    for expert_id, keywords in KEYWORD_MAP.items()
}

# 관계 명사는 주제보다 배경으로 섞여 들어오는 경우가 많다.
# "결혼하고 첫 자가 6억대 vs 8억대"는 금전 질문인데 '결혼' 하나 때문에 love로 갔다.
# 이런 낱말은 반 표만 줘서 실제 주제 키워드를 못 이기게 한다.
_WEAK_KEYWORDS = {
    '엄마', '아빠', '부모', '가족', '형제', '자매', '친구', '동생',
    '오빠', '언니', '누나', '형이', '형한테', '관계', '사람',
    '그 사람', '저 사람', '상대', '결혼', '마음', '진심',
}
_WEAK_WEIGHT = 0.5


def keyword_match(question: str) -> Optional[str]:
    """키워드 점수가 가장 높은 expert. 매칭 없으면 None"""
    if not question:
        return None

    q_lower = question.lower()
    scores = {expert_id: 0.0 for expert_id in KEYWORD_MAP}

    for expert_id, patterns in _KEYWORD_PATTERNS.items():
        for kw, pat in patterns:
            if pat.search(q_lower):
                scores[expert_id] += _WEAK_WEIGHT if kw in _WEAK_KEYWORDS else 1

    max_score = max(scores.values())
    if max_score == 0:
        return None

    # "오늘 운세"처럼 시간 표현이 명시되면 주제 키워드보다 우선.
    # 없으면 "오늘 하루 어떤 일이 있을까?"가 '일이' 때문에 career로 간다.
    EXPLICIT_TIME = ('오늘', '내일', '모레', '이번 주', '이번주',
                     '이번 달', '이번달', '올해', '내년', '주간운세', '월간운세')
    if scores['daily'] > max([v for k, v in scores.items() if k != 'daily']) \
            and any(t in q_lower for t in EXPLICIT_TIME):
        return 'daily'

    # 동점이면 love > self > career > money > daily 순
    priority = ['love', 'self', 'career', 'money', 'daily']
    for expert_id in priority:
        if scores[expert_id] == max_score:
            return expert_id

    return None


_EMBED_CONFIDENCE_THRESHOLD = 0.55
_FALLBACK_EXPERT = 'daily'


def get_expert(question: str, return_meta: bool = False):
    """expert_id 반환. return_meta=True면 판단 근거가 담긴 dict 반환"""
    if not question or not question.strip():
        if return_meta:
            return {'primary': _FALLBACK_EXPERT, 'scores': {}, 'used': 'fallback', 'reason': 'empty'}
        return _FALLBACK_EXPERT

    keyword_choice = keyword_match(question)

    # 임베딩은 기본 OFF. 첫 로드가 17초 걸려 첫 응답이 30초를 넘겼고, 키워드만으로도 분류가 충분했음
    embedding_top = None
    embedding_score = 0.0
    embedding_ranked = []
    import os
    if os.getenv('USE_EMBEDDING_ROUTER', 'false').lower() == 'true':
        try:
            from .embedder import ExpertEmbedder
            embedder = ExpertEmbedder()
            embedding_ranked = embedder.rank_experts(question, top_k=3)
            if embedding_ranked:
                embedding_top, embedding_score = embedding_ranked[0]
        except Exception as e:
            logger.warning(f"[router] 임베딩 실패: {e}. 키워드만 사용")

    if keyword_choice and embedding_top:
        if keyword_choice == embedding_top:
            chosen, used = keyword_choice, 'keyword+embedding'
        elif embedding_score >= _EMBED_CONFIDENCE_THRESHOLD:
            # 임베딩 점수가 높으면 임베딩 쪽을 따름
            chosen, used = embedding_top, 'embedding-strong'
        else:
            chosen, used = keyword_choice, 'keyword'
    elif keyword_choice:
        chosen, used = keyword_choice, 'keyword-only'
    elif embedding_top and embedding_score >= _EMBED_CONFIDENCE_THRESHOLD:
        chosen, used = embedding_top, 'embedding-only'
    else:
        chosen, used = _FALLBACK_EXPERT, 'fallback'

    if return_meta:
        return {
            'primary': chosen,
            'used': used,
            'keyword_choice': keyword_choice,
            'embedding_top': embedding_top,
            'embedding_score': embedding_score,
            'embedding_ranked': embedding_ranked,
        }
    return chosen
