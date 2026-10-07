"""임베딩 기반 expert 선택

expert별 대표 문구 임베딩 평균과 질문 임베딩의 cosine 유사도로 고름.
모델은 intfloat/multilingual-e5-small.
"""
import logging
import numpy as np
from typing import Optional

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = 'intfloat/multilingual-e5-small'

# expert별 대표 문구. 같은 의도의 여러 표현을 모아둠
EXPERT_PROTOTYPES = {
    'love': [
        '좋아하는 사람이 날 어떻게 생각할까',
        '이별한 사람이랑 다시 만날 수 있을까',
        '짝사랑하는데 고백해도 될까',
        '남친 여친이랑 자꾸 싸워',
        '소개팅 한 사람과 잘 될까',
        '엄마 아빠랑 부딪쳐서 힘들어',
        '친구가 변한 것 같아',
        '재회 가능성 있을까',
        '결혼 이 사람과 해도 될까',
        '바람피우는 것 같아 어떡해',
        '오래된 연인 권태기야',
        'love relationship boyfriend girlfriend dating breakup family friend',
    ],
    'career': [
        '회사 그만둘까 이직할까',
        '이 일 적성에 맞을까',
        '취업이 안 돼 어떡해',
        '면접 잘 볼 수 있을까',
        '창업 도전해도 될까',
        '승진할 수 있을까',
        '번아웃 왔어 쉬어야 할까',
        '이 회사 더 다녀도 될까',
        '진로 어떻게 정해야 할까',
        '학교 자퇴할까 다닐까',
        '대학원 갈까 취업할까',
        'career job interview promotion startup burnout work',
    ],
    'money': [
        '돈이 모이질 않아',
        '투자 어떻게 해야 할까',
        '주식 코인 사도 될까',
        '이번 달 재정 어때',
        '빚이 많은데 어떡해',
        '저축 어떻게 늘릴까',
        '집 살 수 있을까',
        '재물운 좋을까',
        '돈 걱정으로 잠 못 자',
        '소비 줄여야 하는데 안 돼',
        'money finance investment savings debt stocks crypto',
    ],
    'self': [
        '내가 뭘 원하는지 모르겠어',
        '내 인생 뭐가 잘못된 걸까',
        '왜 이렇게 살고 있는지',
        '나는 어떤 사람일까',
        '미래가 막막해',
        '우울해 의욕이 없어',
        '내 길을 못 찾겠어',
        '자존감이 낮아',
        '나를 사랑하기 어려워',
        '삶의 의미가 뭘까',
        '내가 정말 행복할까',
        'self identity purpose meaning depression inner growth',
    ],
    'daily': [
        '오늘의 운세 알려줘',
        '이번 주 어떤 흐름일까',
        '오늘 카드 뽑아줘',
        '오늘 어떤 일이 있을까',
        '내일 시험 잘 볼까',
        '주말 여행 가도 될까',
        '오늘 무엇을 조심해야 할까',
        '이번 달 전체 흐름',
        '오늘의 럭키 컬러',
        'today weekly daily fortune horoscope general',
    ],
}


class ExpertEmbedder:
    """싱글톤. 모델은 첫 호출 때 로드"""

    _instance: Optional['ExpertEmbedder'] = None
    _model = None
    _prototype_embeddings = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _load_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            logger.info(f"[expert-embedder] 모델 로드 중: {EMBEDDING_MODEL}")
            self._model = SentenceTransformer(EMBEDDING_MODEL)
            self._build_prototype_embeddings()
            logger.info("[expert-embedder] 모델 로드 완료")

    def _build_prototype_embeddings(self):
        """expert별 대표 문구 임베딩 평균"""
        proto_emb = {}
        for expert_id, prototypes in EXPERT_PROTOTYPES.items():
            # e5는 'query: ' / 'passage: ' prefix를 붙여야 성능이 나옴
            texts = [f"passage: {p}" for p in prototypes]
            embeddings = self._model.encode(texts, normalize_embeddings=True)
            proto_emb[expert_id] = np.mean(embeddings, axis=0)
        self._prototype_embeddings = proto_emb

    def rank_experts(self, question: str, top_k: int = 3) -> list[tuple[str, float]]:
        """[(expert_id, cosine 점수), ...] 높은 순"""
        self._load_model()
        if not question or not question.strip():
            return [('daily', 0.5)]

        q_embedding = self._model.encode(f"query: {question}", normalize_embeddings=True)

        scores = {}
        for expert_id, proto_emb in self._prototype_embeddings.items():
            scores[expert_id] = float(np.dot(q_embedding, proto_emb))

        ranked = sorted(scores.items(), key=lambda x: -x[1])
        return ranked[:top_k]

    def get_top_expert(self, question: str) -> tuple[str, float]:
        """1등 expert와 점수"""
        ranked = self.rank_experts(question, top_k=1)
        return ranked[0] if ranked else ('daily', 0.5)
