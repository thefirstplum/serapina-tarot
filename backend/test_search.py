#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""웹 검색 기능 테스트"""

from duckduckgo_search import DDGS

# 테스트 쿼리들
test_queries = [
    "한국 대통령 2025",
    "윤석열 대통령",
    "대한민국 현재 대통령",
]

for query in test_queries:
    print(f"\n{'='*60}")
    print(f"🔍 검색어: '{query}'")
    print('='*60)

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, region='kr-kr', max_results=3))

            if results:
                print(f'✅ {len(results)}개 결과 발견\n')
                for i, result in enumerate(results, 1):
                    print(f'{i}. {result["title"]}')
                    print(f'   {result["body"][:150]}...')
                    print(f'   출처: {result["href"]}\n')
            else:
                print('⚠️ 검색 결과 없음')
    except Exception as e:
        print(f'❌ 검색 실패: {e}')
