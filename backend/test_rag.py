#!/usr/bin/env python3
"""
RAG 시스템 테스트 스크립트
"""

import asyncio
from rag_search import get_rag_search, search_tarot_knowledge


async def test_rag():
    """RAG 시스템 테스트"""

    print("=" * 60)
    print("타로 RAG 시스템 테스트")
    print("=" * 60)

    # RAG 인스턴스 로드
    try:
        rag = get_rag_search()
        if rag is None:
            print("❌ RAG 시스템을 로드할 수 없습니다.")
            return

        stats = rag.get_stats()
        print(f"\n✅ RAG 시스템 로드 성공")
        print(f"   컬렉션: {stats['collection_name']}")
        print(f"   총 청크: {stats['total_chunks']}개")
        print(f"   저장 경로: {stats['persist_dir']}")

    except Exception as e:
        print(f"❌ RAG 시스템 로드 실패: {e}")
        return

    # 테스트 질문들
    test_queries = [
        "연애운세 보고 싶어",
        "짝사랑하는 사람이 있는데 내 마음을 알까?",
        "이별 후 재회 가능성은?",
        "오늘의 운세는?",
        "취업 잘 될까?",
        "메이저 아르카나 죽음 카드의 의미는?"
    ]

    for idx, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"테스트 {idx}: {query}")
        print(f"{'='*60}")

        try:
            # RAG 검색 (raw documents)
            docs = rag.search(query, n_results=3, min_relevance=0.0)

            print(f"\n발견된 문서: {len(docs)}개")
            for i, doc in enumerate(docs, 1):
                print(f"  {i}. 유사도: {doc['relevance']:.3f} (길이: {len(doc['content'])} chars)")

            # 포맷된 컨텍스트
            context = rag.format_context(docs)

            if context:
                print(f"\n✅ 관련 지식 발견 ({len(context)} chars):")
                print("-" * 60)
                # 처음 500자만 출력
                preview = context[:500] + "..." if len(context) > 500 else context
                print(preview)
            else:
                print("\n⚠️ 관련 지식을 찾을 수 없습니다.")

        except Exception as e:
            print(f"\n❌ 검색 실패: {e}")

    print(f"\n{'='*60}")
    print("테스트 완료!")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(test_rag())
