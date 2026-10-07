# -*- coding: utf-8 -*-
"""기동 시 자체 점검

이 서비스는 주요 컴포넌트를 try/except로 감싸고 실패하면 로그 한 줄만 남긴 채 계속 돈다.
그래서 아래 문제들이 길게는 1년 가까이 드러나지 않았다.
- 마이너 아르카나 56장의 카드 설명이 비어 있었음
- chromadb import 실패로 RAG가 꺼져 있었음
- RAG 유사도 계산 오류로 검색 결과가 항상 0건이었음
LLM이 빈자리를 그럴듯하게 메워서 출력만 봐서는 알 수 없었다.
기동할 때 각 컴포넌트를 한 번씩 써 보고 결과를 눈에 띄게 찍는다.

사용:
    await run_selfcheck()   # startup 이벤트에서 호출
    GET /selfcheck          # 운영 중 확인
"""

import asyncio
import os
import traceback

# 점검 결과 캐시 (/selfcheck 엔드포인트가 재사용)
LAST_RESULT = {}


def _ok(name, detail):
    return {"name": name, "status": "ok", "detail": detail}


def _warn(name, detail):
    return {"name": name, "status": "warn", "detail": detail}


def _fail(name, detail):
    return {"name": name, "status": "fail", "detail": detail}


# 개별 점검

def check_card_data():
    """78장이 모두 실제 내용을 갖고 있는지. 필드가 비면 리딩이 일반론이 된다."""
    try:
        from card_data import CARD_DB, CARD_MAPPING, CARD_DESCRIPTIONS
    except Exception as e:
        return _fail("card_data", f"import 실패: {e}")

    if len(CARD_DB) != 78:
        return _fail("card_data", f"카드 {len(CARD_DB)}장 (78장이어야 함)")

    required = ["upright", "reversed", "love", "career", "money",
                "advice", "timing", "timing_scale", "yesno",
                "up_keys", "rev_keys", "image"]
    empty = {}
    for cid, card in CARD_DB.items():
        missing = [f for f in required if not card.get(f)]
        if missing:
            empty[cid] = missing
    if empty:
        sample = list(empty.items())[:3]
        return _fail("card_data",
                     f"{len(empty)}장에 빈 필드 있음 (예: {sample})")

    # 하위호환 매핑도 확인. 여기가 비면 프롬프트에 '설명이 없어'가 들어간다
    no_desc = [n for n in CARD_MAPPING.values() if n not in CARD_DESCRIPTIONS]
    if no_desc:
        return _fail("card_data",
                     f"CARD_DESCRIPTIONS 누락 {len(no_desc)}장 (예: {no_desc[:3]})")

    return _ok("card_data", f"78장 × {len(required)}필드 / 매핑 {len(CARD_DESCRIPTIONS)}개")


def check_spreads():
    """스프레드 정의와 카드 수가 일치하는지."""
    try:
        from spreads import SPREADS, get_spread, resolve_spread_name
    except Exception as e:
        return _fail("spreads", f"import 실패: {e}")

    bad = []
    for name in SPREADS:
        try:
            cnt, pos, _ = get_spread(name, "", None)
            if cnt != len(pos):
                bad.append(f"{name}({cnt}≠{len(pos)})")
        except Exception as e:
            bad.append(f"{name}(오류:{e})")
    if bad:
        return _fail("spreads", f"카드수 불일치: {bad}")

    # 이름 정규화가 살아있는지 (LLM 이 흘려 쓴 이름 대응)
    if resolve_spread_name("속마음운세") != "속마음":
        return _warn("spreads", "이름 정규화가 동작하지 않음")

    return _ok("spreads", f"{len(SPREADS)}종 정합")


def check_expert_router():
    """질문 도메인 라우팅이 살아있는지. 틀리면 엉뚱한 카드 의미가 들어간다."""
    try:
        from experts.router import get_expert
    except Exception as e:
        return _fail("expert_router", f"import 실패: {e}")

    cases = [
        ("썸남한테 먼저 연락해도 될까?", "love"),
        ("오늘 하루 어떤 일이 있을까?", "daily"),
        ("이직할까 고민이야", "career"),
        ("주식 살까", "money"),
    ]
    wrong = [f"{q}: {get_expert(q)}(기대 {e})" for q, e in cases if get_expert(q) != e]
    if wrong:
        return _warn("expert_router", f"오분류 {len(wrong)}/{len(cases)}: {wrong}")
    return _ok("expert_router", f"샘플 {len(cases)}건 정확")


def check_rag():
    """RAG가 로드되는지에 더해 실제로 결과를 돌려주는지까지 확인.

    유사도 계산이 틀려 항상 0건을 돌려주던 버그는 로드는 성공한 상태로 숨어 있었다.
    """
    if os.getenv("DISABLE_RAG", "").lower() == "true":
        return _ok("rag", "비활성화됨 (DISABLE_RAG=true)")
    try:
        from rag_search import get_rag_search
    except Exception as e:
        return _fail("rag", f"import 실패: {e}")

    rag = get_rag_search()
    if rag is None:
        return _fail("rag", "인스턴스 생성 실패 (인덱스 없음 또는 의존성 충돌)")

    try:
        count = rag.collection.count()
    except Exception as e:
        return _fail("rag", f"컬렉션 접근 실패: {e}")
    if count == 0:
        return _fail("rag", "인덱스가 비어 있음")

    # 실제 검색까지 해 본다. 0건이면 로드돼도 쓸모가 없다
    try:
        hits = rag.search("연애운이 궁금해", n_results=2)
    except Exception as e:
        return _fail("rag", f"검색 실패: {e}")
    if not hits:
        return _fail("rag",
                     f"로드는 됐으나 검색 결과 0건 "
                     f"(청크 {count}개, 유사도 계산이나 임계값 확인 필요)")

    top = hits[0].get("relevance", 0)
    return _ok("rag", f"청크 {count}개 / 샘플 검색 {len(hits)}건 (최고 관련도 {top})")


def check_encryption():
    """암호화 왕복이 되는지. 실패하면 리딩 저장이 통째로 막힌다."""
    try:
        from encryption import get_encryption
        enc = get_encryption()
        probe = "자체점검 문자열 ✓"
        if enc.decrypt_text(enc.encrypt_text(probe)) != probe:
            return _fail("encryption", "암복호화 왕복 불일치")
        return _ok("encryption", "암복호화 왕복 정상")
    except Exception as e:
        return _fail("encryption", f"{e}")


async def check_llm():
    """LLM 엔드포인트가 응답하는지 (모델 생성까지는 하지 않음)."""
    url = os.getenv("OLLAMA_API_URL", "")
    if not url:
        return _warn("llm", "OLLAMA_API_URL 미설정")
    try:
        import httpx
        async with httpx.AsyncClient(timeout=10.0) as c:
            r = await c.get(url.replace("/api/chat", "/api/tags"))
        if r.status_code != 200:
            return _fail("llm", f"HTTP {r.status_code}")
        names = [m["name"] for m in r.json().get("models", [])]
        want = os.getenv("OLLAMA_MODEL_HEAVY") or os.getenv("OLLAMA_MODEL") or ""
        if want and not any(want.split(":")[0] in n for n in names):
            return _fail("llm", f"모델 '{want}' 없음 (보유: {names})")
        return _ok("llm", f"{len(names)}개 모델 / 사용: {want}")
    except Exception as e:
        return _fail("llm", f"연결 실패: {e}")


# 실행

async def run_selfcheck(verbose=True):
    """모든 점검 실행. 결과 dict 반환 + 콘솔에 크게 출력."""
    global LAST_RESULT

    results = []
    for fn in (check_card_data, check_spreads, check_expert_router,
               check_rag, check_encryption):
        try:
            results.append(fn())
        except Exception as e:
            results.append(_fail(fn.__name__, f"점검 자체 오류: {e}\n{traceback.format_exc()}"))
    try:
        results.append(await check_llm())
    except Exception as e:
        results.append(_fail("llm", f"점검 자체 오류: {e}"))

    fails = [r for r in results if r["status"] == "fail"]
    warns = [r for r in results if r["status"] == "warn"]

    if verbose:
        icon = {"ok": "✅", "warn": "⚠️ ", "fail": "❌"}
        print("\n" + "=" * 58)
        print("기동 자체 점검")
        print("=" * 58)
        for r in results:
            print(f"{icon[r['status']]} {r['name']:14s} {r['detail']}")
        print("-" * 58)
        if fails:
            print(f"!!! 점검 실패 {len(fails)}건. 리딩 품질이 떨어진 상태로 동작합니다")
            for r in fails:
                print(f"   ❌ {r['name']}: {r['detail']}")
            print("!!! 위 항목을 고치기 전까지 결과물을 믿지 마세요")
        elif warns:
            print(f"⚠️  경고 {len(warns)}건. 동작은 하지만 확인 필요")
        else:
            print("✅ 전 항목 정상")
        print("=" * 58 + "\n", flush=True)

    LAST_RESULT = {
        "healthy": not fails,
        "fail_count": len(fails),
        "warn_count": len(warns),
        "checks": results,
    }
    return LAST_RESULT
