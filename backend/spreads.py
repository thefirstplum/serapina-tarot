# -*- coding: utf-8 -*-
"""타로 스프레드 정의와 시간 기반 카드 위치 생성

질문한 시간창을 벗어나지 않는 게 원칙이다.
  "이번 주 운세"인데 카드 자리에 '다음 주 월요일'이 섞여 나오면 안 된다.
  남은 기간이 너무 짧아 3등분이 무의미하면, 창을 통째로 다음 주기로 옮기고
  라벨에 그 사실을 분명히 밝힌다(섞지 않는다).
"""

from datetime import datetime, timedelta
import calendar
import re


# 시간 기반 위치 생성

def _target_day(question):
    """일일운세가 가리키는 날짜 오프셋과 라벨"""
    q = question or ""
    if "글피" in q:
        return 3, "글피"
    if "모레" in q:
        return 2, "모레"
    if "내일" in q:
        return 1, "내일"
    return 0, "오늘"


def daily_positions(question="", now=None):
    """하루를 시간대로 3등분. 대상 날짜 밖으로 절대 안 나간다."""
    offset, label = _target_day(question)
    now = now or datetime.now()

    # 오늘 질문인데 이미 늦은 시간이면 남은 시간대만 쪼갠다
    if offset == 0:
        h = now.hour
        if h >= 18:
            return [f"{label} 저녁", f"{label} 밤", f"{label} 마무리"], label
        if h >= 12:
            return [f"{label} 오후", f"{label} 저녁", f"{label} 밤"], label
    return [f"{label} 오전", f"{label} 오후", f"{label} 저녁"], label


def weekly_positions(question="", now=None):
    """이번 주(월~일) 안에서만 3등분.
    남은 날이 2일 이하면 '다가오는 한 주'로 창을 옮긴다."""
    now = now or datetime.now()
    wd = now.weekday()            # 0=월, 6=일
    remaining = 6 - wd            # 오늘 제외 남은 날 수

    if "다음 주" in (question or "") or remaining <= 1:
        # 창을 통째로 다음 주로. 이번 주와 섞지 않는다.
        return (["다음 주 초 (월~화)", "다음 주 중반 (수~목)", "다음 주 후반 (금~일)"],
                "다음 주")

    if wd <= 1:       # 월·화: 주 전체가 남음
        return (["주초 (월~화)", "주중 (수~목)", "주말 (금~일)"], "이번 주")
    if wd <= 3:       # 수·목: 남은 절반
        return (["오늘~내일", "주 후반 (금)", "주말 (토~일)"], "이번 주 남은 기간")
    # 금·토: 주말만 남음
    return (["오늘", "토요일", "일요일"], "이번 주 남은 기간")


def monthly_positions(question="", now=None):
    """이번 달 안에서만. 남은 기간이 짧으면 다음 달로 창을 옮긴다."""
    now = now or datetime.now()
    d = now.day
    last = calendar.monthrange(now.year, now.month)[1]

    if "다음 달" in (question or "") or (last - d) <= 5:
        return (["다음 달 월초 (1~10일)", "다음 달 중순 (11~20일)",
                 "다음 달 월말 (21일~)", "다음 달 핵심 흐름", "조언"], "다음 달")

    if d <= 10:
        slots = ["월초 (1~10일)", "중순 (11~20일)", "월말 (21일~)"]
    elif d <= 20:
        slots = [f"남은 중순 ({d}~20일)", "월말 (21~25일)", "월말 마무리 (26일~)"]
    else:
        slots = [f"남은 기간 ({d}~{last}일) 초반", "중반", "마무리"]
    return (slots + ["이번 달 핵심 흐름", "조언"], "이번 달")


def yearly_positions(question="", now=None):
    """올해를 분기로 쪼개되, 이미 지난 분기는 넣지 않는다.
    남은 분기가 1개뿐이면 내년으로 창을 옮긴다."""
    now = now or datetime.now()
    q = (now.month - 1) // 3 + 1      # 현재 분기 1~4

    QLABEL = {1: "1분기 (1~3월)", 2: "2분기 (4~6월)",
              3: "3분기 (7~9월)", 4: "4분기 (10~12월)"}

    if "내년" in (question or "") or q == 4:
        return (["내년 1분기 (1~3월)", "내년 2분기 (4~6월)",
                 "내년 3분기 (7~9월)", "내년 4분기 (10~12월)", "내년 핵심 조언"],
                "내년")

    remaining = [QLABEL[i] for i in range(q, 5)]
    if q > 1:
        remaining[0] = "남은 " + remaining[0]
    # 분기 + 핵심 + 조언 = 항상 5장으로 맞춘다
    pos = remaining[:4]
    while len(pos) < 4:
        pos.append(["올해 핵심 기회", "올해 주의할 점", "올해 조언"][len(pos) - len(remaining)])
    pos.append("올해 조언")
    return (pos[:5], "올해")


# 스프레드 정의. time_fn이 있으면 위치를 지금 시점 기준으로 만든다.

SPREADS = {
    # 시간 단위
    "일일운세":   {"count": 3, "time_fn": daily_positions,
                "desc": "'오늘·내일·모레' 하루 단위"},
    "주간운세":   {"count": 3, "time_fn": weekly_positions,
                "desc": "'이번 주·다음 주' 일주일 단위"},
    "월간운세":   {"count": 5, "time_fn": monthly_positions,
                "desc": "'이번 달·다음 달' 한 달 단위"},
    "연간운세":   {"count": 5, "time_fn": yearly_positions,
                "desc": "'올해·내년' 분기별 1년 단위"},

    # 연애
    "연애운세":   {"count": 4, "pos": ["현재 상황", "상대방 마음", "앞으로 전개", "조언"],
                "desc": "연애 전반"},
    "짝사랑운세": {"count": 4, "pos": ["내 마음 상태", "상대방 마음", "다가갈 방법", "앞으로 전망"],
                "desc": "짝사랑, 좋아하는 사람"},
    "썸운세":     {"count": 4, "pos": ["현재 썸 상황", "상대 진심도", "발전 가능성", "조언"],
                "desc": "썸, 애매한 관계, 밀당"},
    "사귀는중운세": {"count": 4, "pos": ["우리 관계", "상대방 마음", "주의할 점", "앞으로"],
                "desc": "남친/여친과의 관계"},
    "이별/재회운세": {"count": 3, "pos": ["현재 상대 마음", "재회 가능성", "나아갈 방향"],
                "desc": "헤어짐, 재회 가능성"},
    "소개팅/만남운세": {"count": 3, "pos": ["만남 가능성", "좋은 인연 시기", "주의사항"],
                "desc": "새로운 인연 만날 가능성"},

    # 생활
    "진로운세":   {"count": 3, "pos": ["현재 상황", "기회", "조언"], "desc": "직장, 이직, 진로"},
    "재물운세":   {"count": 3, "pos": ["현재 재정", "돈 들어올 방향", "주의할 점"], "desc": "돈, 재정"},
    "건강운세":   {"count": 3, "pos": ["현재 건강", "주의할 점", "개선 방법"], "desc": "건강, 컨디션"},
    "학업운세":   {"count": 3, "pos": ["현재 학습 상태", "집중할 부분", "시험 전망"], "desc": "시험, 공부, 성적"},
    "우정운세":   {"count": 3, "pos": ["현재 관계", "주의할 점", "더 좋아지려면"], "desc": "친구 관계, 우정"},

    # 기본
    "예스/노":    {"count": 1, "pos": ["답"], "desc": "아주 단순한 예/아니오 단답 (카드 1장)"},
    "가능성":     {"count": 4,
                "pos": ["지금 상황", "되게 만드는 힘", "막고 있는 것", "결론"],
                "desc": "'될까?', '가능할까?' — 가능 여부를 근거까지 보여줄 때"},
    "과거-현재-미래": {"count": 3, "pos": ["과거", "현재", "미래"], "desc": "흐름을 보는 기본형"},

    # 질문 의도별 (2026-09 추가)
    "선택":       {"count": 5,
                "pos": ["지금 상황", "A를 골랐을 때", "B를 골랐을 때",
                        "못 보고 있는 변수", "카드가 기우는 쪽"],
                "desc": "'A냐 B냐', 둘 중 하나를 골라야 하는 질문"},
    "시기":       {"count": 3,
                "pos": ["지금 막고 있는 것", "언제 풀리는지", "그때 오는 형태"],
                "desc": "'언제?', '얼마나 걸려?' 시점을 묻는 질문"},
    "속마음":     {"count": 4,
                "pos": ["그 사람의 겉모습", "속으로 하는 생각", "나에 대한 감정", "말 못 하는 이유"],
                "desc": "'그 사람 속마음', 상대 심리만 집중해서 볼 때"},
    "원인-해결":  {"count": 4,
                "pos": ["겉으로 보이는 문제", "진짜 원인", "해결의 실마리", "결과"],
                "desc": "'왜 이럴까', 문제의 근본 원인을 찾는 질문"},
    "관계":       {"count": 5,
                "pos": ["나의 입장", "상대의 입장", "둘 사이에 흐르는 것",
                        "이 관계의 과제", "앞으로"],
                "desc": "가족·친구·동료 등 사람 사이 역학을 볼 때"},
    "켈틱크로스": {"count": 10,
                "pos": ["현재 상황", "당면 과제", "의식하는 것", "무의식 밑바탕",
                        "지나간 것", "다가올 것", "나의 태도", "주변 환경",
                        "희망과 두려움", "최종 결과"],
                "desc": "복잡하고 오래된 고민을 깊게 볼 때 (10장)"},
}


def get_spread(name, question="", now=None):
    """스프레드 이름으로 (카드 수, 위치 목록, 시간창 라벨)을 돌려준다"""
    spec = SPREADS.get(name)
    if not spec:
        return None
    if "time_fn" in spec:
        pos, window = spec["time_fn"](question, now)
        return spec["count"], pos, window
    return spec["count"], list(spec["pos"]), None


def build_catalog_text():
    """LLM 프롬프트에 넣을 스프레드 목록. SPREADS 와 항상 동기화된다."""
    return "\n".join(
        f"- {name} ({spec['count']}장): {spec['desc']}"
        for name, spec in SPREADS.items()
    )


def resolve_spread_name(raw):
    """LLM이 뱉은 스프레드 이름을 테이블 키로 정규화한다.

    LLM은 '속마음운세'(접미사 추가), '시기 (3장)'(장수 포함) 처럼
    카탈로그 표기를 그대로 따라오는 경우가 잦다. 이걸 못 잡으면
    조용히 기본 스프레드로 폴백돼서 엉뚱한 리딩이 나간다.
    """
    if not raw:
        return None
    name = str(raw).strip()

    if name in SPREADS:
        return name

    # "시기 (3장)"에서 괄호 제거
    name = re.sub(r"\s*\(.*?\)\s*", "", name).strip()
    if name in SPREADS:
        return name

    # "속마음운세"와 "속마음"을 같은 것으로
    if name.endswith("운세") and name[:-2] in SPREADS:
        return name[:-2]
    if name + "운세" in SPREADS:
        return name + "운세"

    # 공백/구분자 무시 후 대조
    norm = lambda s: re.sub(r"[\s\-/]", "", s)
    target = norm(name)
    for key in SPREADS:
        if norm(key) == target:
            return key
    for key in SPREADS:
        if target and (target in norm(key) or norm(key) in target):
            return key
    return None
