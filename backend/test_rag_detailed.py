#!/usr/bin/env python3
"""
RAG 시스템 상세 테스트 - 실제 유사도와 검색 품질 확인
"""

import asyncio
from rag_search import TarotRAGSearch
import numpy as np


def test_embedding_similarity():
    """임베딩 모델 자체의 유사도 계산 테스트"""
    print("=" * 60)
    print("1. 임베딩 모델 유사도 테스트")
    print("=" * 60)

    rag = TarotRAGSearch()

    # 테스트 쿼리와 문서
    test_cases = [
        ("연애운세", "연애 카드 해석 방법"),
        ("연애운세", "건강 운세 보는 법"),
        ("짝사랑", "짝사랑 상대방 마음"),
        ("짝사랑", "주식 투자 방법")
    ]

    for query, doc in test_cases:
        query_emb = rag.embedding_model.encode(query)
        doc_emb = rag.embedding_model.encode(doc)

        # 코사인 유사도 계산
        similarity = np.dot(query_emb, doc_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(doc_emb))

        print(f"\nQuery: '{query}' vs Doc: '{doc}'")
        print(f"  → 유사도: {similarity:.4f}")


def test_chromadb_search():
    """ChromaDB 검색 결과 상세 분석"""
    print("\n" + "=" * 60)
    print("2. ChromaDB 검색 상세 테스트")
    print("=" * 60)

    rag = TarotRAGSearch()

    test_queries = [
        "연애운세 보고 싶어",
        "짝사랑하는 사람 마음",
        "이별 후 재회 가능성",
        "메이저 아르카나 죽음 카드"
    ]

    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")

        # ChromaDB raw 결과
        query_embedding = rag.embedding_model.encode(query)
        results = rag.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=5
        )

        print(f"\n발견된 문서: {len(results['documents'][0])}개")

        if results['distances']:
            print(f"\n거리 값:")
            for idx, dist in enumerate(results['distances'][0], 1):
                print(f"  {idx}. 거리: {dist:.6f}")

        if results['documents']:
            print(f"\n문서 미리보기:")
            for idx, doc in enumerate(results['documents'][0][:3], 1):
                preview = doc[:150].replace('\n', ' ')
                print(f"  {idx}. {preview}...")

        if results['metadatas']:
            print(f"\n메타데이터:")
            for idx, meta in enumerate(results['metadatas'][0][:3], 1):
                print(f"  {idx}. video_id={meta.get('video_id')}, keywords={meta.get('keywords', '')[:50]}")


def test_rag_search_quality():
    """RAG 검색 품질 테스트 - 실제 사용 시나리오"""
    print("\n" + "=" * 60)
    print("3. RAG 검색 품질 테스트")
    print("=" * 60)

    rag = TarotRAGSearch()

    scenarios = [
        {
            "query": "썸타는 사람이 나를 좋아할까?",
            "expected_keywords": ["썸", "마음", "좋아", "연애", "감정"]
        },
        {
            "query": "이번 주 금전운은?",
            "expected_keywords": ["금전", "돈", "재물", "펜타클"]
        },
        {
            "query": "전 남자친구와 재회 가능성",
            "expected_keywords": ["재회", "이별", "전 남", "다시", "연락"]
        }
    ]

    for scenario in scenarios:
        query = scenario["query"]
        expected = scenario["expected_keywords"]

        print(f"\n{'='*60}")
        print(f"시나리오: {query}")
        print(f"기대 키워드: {', '.join(expected)}")
        print(f"{'='*60}")

        # RAG 검색
        docs = rag.search(query, n_results=3, min_relevance=0.0)

        if docs:
            print(f"\n✅ {len(docs)}개 문서 발견")

            # 키워드 매칭 확인
            all_content = " ".join([d["content"] for d in docs])
            matched_keywords = [kw for kw in expected if kw in all_content]

            print(f"매칭된 키워드: {', '.join(matched_keywords) if matched_keywords else '없음'}")
            print(f"매칭률: {len(matched_keywords)}/{len(expected)} ({len(matched_keywords)/len(expected)*100:.0f}%)")

            # 문서 내용 샘플
            print(f"\n문서 1 샘플 (200자):")
            print(docs[0]["content"][:200])
        else:
            print("\n❌ 문서를 찾지 못했습니다")


def test_actual_usage():
    """실제 API 사용 시나리오 테스트"""
    print("\n" + "=" * 60)
    print("4. 실제 API 사용 시나리오")
    print("=" * 60)

    rag = TarotRAGSearch()

    questions = [
        "오늘 연애운이 궁금해",
        "시험 합격할 수 있을까?",
        "이직 타이밍이 맞나?"
    ]

    for question in questions:
        print(f"\n{'='*60}")
        print(f"사용자 질문: {question}")
        print(f"{'='*60}")

        docs = rag.search(question, n_results=3, min_relevance=0.0)
        context = rag.format_context(docs, max_length=1000)

        if context:
            print(f"\n✅ AI에게 제공될 컨텍스트 ({len(context)} chars):")
            print("-" * 60)
            preview = context[:400] + "..." if len(context) > 400 else context
            print(preview)
        else:
            print("\n❌ 컨텍스트 없음")


if __name__ == "__main__":
    try:
        # 1. 임베딩 모델 자체 테스트
        test_embedding_similarity()

        # 2. ChromaDB 검색 상세 분석
        test_chromadb_search()

        # 3. RAG 검색 품질
        test_rag_search_quality()

        # 4. 실제 사용 시나리오
        test_actual_usage()

        print("\n" + "=" * 60)
        print("✅ 모든 테스트 완료!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
