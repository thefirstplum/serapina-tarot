"""
RAG 검색 모듈

타로 질문에 대해 관련 지식을 벡터 DB에서 검색
"""

import numpy as np
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from pathlib import Path


class TarotRAGSearch:
    """타로 지식 검색"""

    def __init__(
        self,
        collection_name="tarot_knowledge",
        persist_dir="rag_data/chroma_db",
        model_name="jhgan/ko-sroberta-multitask"
    ):
        self.persist_dir = Path(persist_dir)

        if not self.persist_dir.exists():
            raise FileNotFoundError(
                f"RAG 데이터베이스를 찾을 수 없습니다: {persist_dir}\n"
                f"먼저 'python scripts/build_rag_index.py --rebuild' 를 실행하세요."
            )

        self.client = chromadb.PersistentClient(
            path=str(self.persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )

        try:
            self.collection = self.client.get_collection(name=collection_name)
        except Exception as e:
            raise RuntimeError(
                f"컬렉션 '{collection_name}'을 로드할 수 없습니다: {e}\n"
                f"RAG 인덱스를 먼저 구축하세요."
            )

        self.embedding_model = SentenceTransformer(model_name)

    def search(
        self,
        query: str,
        n_results: int = 3,
        min_relevance: float = 0.4
    ) -> List[Dict]:
        """
        질문과 관련된 타로 지식 검색.
        반환: [{"content", "relevance", "metadata"}], relevance 높은 순
        """
        query_embedding = self.embedding_model.encode(query)

        # 아래에서 유사도를 직접 계산하려고 문서 임베딩도 같이 받는다
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results * 2,  # 필터링을 고려해 더 많이 가져옴
            include=["documents", "metadatas", "distances", "embeddings"],
        )

        documents = []

        # 인덱스는 정규화 안 된 768차원 벡터를 L2로 색인해서 distance가 80~190쯤 나온다.
        # 예전 코드는 relevance = max(0, 1 - distance)라 항상 0이었고 결과가 한 건도 안 나갔다.
        # 거리 대신 코사인 유사도(0~1)를 직접 계산한다.
        q_vec = np.asarray(query_embedding, dtype=float)
        q_norm = np.linalg.norm(q_vec)

        if results and results['documents']:
            embeddings = results.get('embeddings') or [[]]
            for idx, doc in enumerate(results['documents'][0]):
                relevance = 0.0
                try:
                    d_vec = np.asarray(embeddings[0][idx], dtype=float)
                    d_norm = np.linalg.norm(d_vec)
                    if q_norm > 0 and d_norm > 0:
                        relevance = float(np.dot(q_vec, d_vec) / (q_norm * d_norm))
                except (IndexError, TypeError, ValueError):
                    # 임베딩을 못 받았으면 거리 순서만 믿고 통과시킨다
                    relevance = min_relevance

                if relevance >= min_relevance:
                    metadata = results['metadatas'][0][idx] if results.get('metadatas') else {}

                    documents.append({
                        "content": doc,
                        "relevance": round(relevance, 3),
                        "metadata": metadata
                    })

        # 유사도 순으로 정렬하고 상위 n개 반환
        documents = sorted(documents, key=lambda x: x['relevance'], reverse=True)[:n_results]

        return documents

    def format_context(self, documents: List[Dict], max_length: int = 2000) -> str:
        """검색 결과를 프롬프트용 텍스트로 합침. max_length(글자 수) 넘으면 자름"""
        if not documents:
            return ""

        context_parts = []
        current_length = 0

        for idx, doc in enumerate(documents, 1):
            keywords = doc['metadata'].get('keywords', '')
            relevance_pct = int(doc['relevance'] * 100)

            doc_text = f"[참고 {idx}] (관련도: {relevance_pct}%)\n{doc['content']}\n"

            if current_length + len(doc_text) > max_length:
                # 넘치면 마지막 문서는 잘라서 넣음
                remaining = max_length - current_length
                if remaining > 100:  # 최소 100자 이상 남았을 때만
                    doc_text = doc_text[:remaining] + "..."
                    context_parts.append(doc_text)
                break

            context_parts.append(doc_text)
            current_length += len(doc_text)

        if not context_parts:
            return ""

        return "\n".join(context_parts)

    def get_stats(self) -> Dict:
        """컬렉션 통계"""
        return {
            "collection_name": self.collection.name,
            "total_chunks": self.collection.count(),
            "persist_dir": str(self.persist_dir)
        }


# 싱글톤 인스턴스 (앱 시작 시 한 번만 로드)
_rag_instance = None


def get_rag_search() -> TarotRAGSearch:
    """RAG 검색 인스턴스 가져오기 (싱글톤)"""
    global _rag_instance

    if _rag_instance is None:
        try:
            _rag_instance = TarotRAGSearch()
            print(f"✅ RAG 검색 시스템 로드됨 (청크: {_rag_instance.collection.count()}개)")
        except Exception as e:
            print(f"⚠️ RAG 시스템 로드 실패: {e}")
            print(f"   RAG 없이 계속 진행합니다.")
            return None

    return _rag_instance


async def search_tarot_knowledge(
    query: str,
    n_results: int = 3,
    format_as_context: bool = True
) -> str:
    """검색 래퍼. format_as_context=False면 문서 리스트 반환, 실패 시 """""
    rag = get_rag_search()

    if rag is None:
        return ""

    try:
        documents = rag.search(query, n_results=n_results)

        if format_as_context:
            return rag.format_context(documents)
        else:
            return documents
    except Exception as e:
        print(f"⚠️ RAG 검색 오류: {e}")
        return ""
