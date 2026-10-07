"""LLM 응답에 섞여 나온 한자/영어를 한국어로 바꾸는 후처리.

1. 사전 매핑 (타로 78장 + 실제로 발견된 누설 패턴)
2. 사전에 없는 단어만 EXAONE으로 단어 단위 치환. 대부분 사전에서 걸러져서 호출은 드묾
3. 영어-한글 경계는 \\b 대신 직접 만든 정규식으로 처리하고 필요하면 띄어쓰기 추가

조사 보정은 부작용이 커서 뺐음.
"""
import re
import json
import logging
import subprocess
from typing import Optional

logger = logging.getLogger(__name__)

REFINE_MODEL = 'exaone3.5:2.4b'
OLLAMA_URL = 'http://localhost:11434/api/chat'

SAFE_ALPHA_TOKENS = {
    'AI', 'MBTI', 'SNS', 'CTA', 'OK', 'PR', 'TV', 'K', 'PWA', 'API', 'UI', 'UX',
    'INFP', 'INFJ', 'INTP', 'INTJ', 'ISFP', 'ISFJ', 'ISTP', 'ISTJ',
    'ENFP', 'ENFJ', 'ENTP', 'ENTJ', 'ESFP', 'ESFJ', 'ESTP', 'ESTJ',
}
KOREAN_PARTICLES = set('을를이가과와은는의도에서로으로만에께서나처럼부터까지보다랑하고이며나마저')

TAROT_DICT = {
    'The Fool': '바보', 'The Magician': '마법사', 'The High Priestess': '여사제',
    'The Empress': '여황제', 'The Emperor': '황제', 'The Hierophant': '교황',
    'The Lovers': '연인', 'The Chariot': '전차', 'Strength': '힘',
    'The Hermit': '은둔자', 'Wheel of Fortune': '운명의 수레바퀴', 'Justice': '정의',
    'The Hanged Man': '매달린 사람', 'Death': '죽음', 'Temperance': '절제',
    'The Devil': '악마', 'The Tower': '탑', 'The Star': '별',
    'The Moon': '달', 'The Sun': '태양', 'Judgement': '심판', 'The World': '세계',
    'Cups': '컵', 'Wands': '완드', 'Swords': '검', 'Pentacles': '펜타클',
    'Ace of Cups': '컵 에이스', 'Ace of Wands': '완드 에이스',
    'Ace of Swords': '검 에이스', 'Ace of Pentacles': '펜타클 에이스',
    'Page of Cups': '컵 시종', 'Page of Wands': '완드 시종',
    'Page of Swords': '검 시종', 'Page of Pentacles': '펜타클 시종',
    'Knight of Cups': '컵 기사', 'Knight of Wands': '완드 기사',
    'Knight of Swords': '검 기사', 'Knight of Pentacles': '펜타클 기사',
    'Queen of Cups': '컵 여왕', 'Queen of Wands': '완드 여왕',
    'Queen of Swords': '검 여왕', 'Queen of Pentacles': '펜타클 여왕',
    'King of Cups': '컵 왕', 'King of Wands': '완드 왕',
    'King of Swords': '검 왕', 'King of Pentacles': '펜타클 왕',
}
for n in ('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten'):
    n_ko = {'Two': '2', 'Three': '3', 'Four': '4', 'Five': '5', 'Six': '6',
            'Seven': '7', 'Eight': '8', 'Nine': '9', 'Ten': '10'}[n]
    for suit_en, suit_ko in [('Cups', '컵'), ('Wands', '완드'), ('Swords', '검'), ('Pentacles', '펜타클')]:
        TAROT_DICT[f'{n} of {suit_en}'] = f'{suit_ko} {n_ko}'

ENGLISH_LEAK_DICT = {
    'distraction': '딴짓', 'observation': '관찰', 'observe': '관찰',
    'physical distance': '물리적 거리', 'physical': '물리적',
    'connection': '연결', 'avoidance': '회피', 'accepted': '받아들임',
    'trusted': '믿는', 'happy': '행복한', 'sad': '슬픈',
    'good': '좋은', 'serious': '진지한',
    'pace': '속도', 'face': '얼굴', 'space': '공간',
    'balance': '균형', 'focus': '집중', 'energy': '에너지',
    'comfort': '편안함', 'control': '주도권', 'choice': '선택',
}

HANJA_LEAK_DICT = {
    '轨迹': '발자취', '付出的': '노력한', '冷静': '차분함',
    '的话题': '에 대한 화제', '替代品': '대체품', '观察': '관찰',
    '对你的': '너에 대한', '短信': '문자', '时间': '시간',
    '人是': '사람은', '人生': '인생', '问题': '문제',
    '关系': '관계', '感情': '감정', '思考': '생각',
    '决定': '결정', '选择': '선택', '机会': '기회',
    '态度': '태도', '方向': '방향', '准备': '준비',
    '行动': '행동', '理解': '이해', '过程': '과정',
    '结果': '결과', '中心': '중심',
}


def detect_leaks(text: str) -> tuple[list, list]:
    english = [w for w in re.findall(r'[a-zA-Z]{2,}', text) if w.upper() not in SAFE_ALPHA_TOKENS]
    hanja = re.findall(r'[一-鿿]+', text)
    return english, hanja


def safe_replace(text: str, pattern_str: str, replacement: str, ignore_case: bool = True) -> str:
    """영어 단어 치환. \\b가 한글 경계를 못 잡아서 앞뒤에 영어가 없는지로 판단.
    뒤에 조사가 바로 붙으면 그대로, 다른 한글이면 공백 추가"""
    flags = re.IGNORECASE if ignore_case else 0

    def add_space_if_needed(match):
        end_pos = match.end()
        if end_pos < len(text) and text[end_pos] in KOREAN_PARTICLES:
            return replacement
        if end_pos < len(text) and '가' <= text[end_pos] <= '힣':
            return replacement + ' '
        return replacement

    pattern = re.compile(rf'(?<![a-zA-Z]){pattern_str}(?![a-zA-Z])', flags)
    return pattern.sub(add_space_if_needed, text)


def safe_replace_hanja(text: str, hanja: str, replacement: str) -> str:
    """한자 치환. 앞뒤에 한글이 붙어 있으면 조사 여부와 상관없이 공백 추가"""
    def smart_replace(match):
        start = match.start()
        end = match.end()
        prefix = ''
        suffix = ''
        if start > 0 and '가' <= text[start-1] <= '힣':
            prefix = ' '
        if end < len(text):
            next_ch = text[end]
            if next_ch in KOREAN_PARTICLES:
                suffix = ''
            elif '가' <= next_ch <= '힣':
                suffix = ' '
        return prefix + replacement + suffix
    return re.sub(re.escape(hanja), smart_replace, text)


def has_jongseong(ch: str) -> bool:
    if not ch:
        return False
    code = ord(ch)
    if 0xAC00 <= code <= 0xD7A3:
        return ((code - 0xAC00) % 28) != 0
    return False


def fix_optional_yi_particle(text: str) -> str:
    """받침 없는 단어 뒤 '이나/이며/이다'의 '이' 탈락 보정 (예: '친구이며'를 '친구며'로)"""
    return re.sub(r'([가-힣])(이나|이며|이라)\b',
                  lambda m: m.group(1) + (m.group(2) if has_jongseong(m.group(1)) else m.group(2)[1:]),
                  text)


def dict_replace(text: str) -> str:
    """사전 매핑 (긴 키부터)"""
    for en, ko in sorted(TAROT_DICT.items(), key=lambda x: -len(x[0])):
        text = safe_replace(text, re.escape(en), ko)
    for en, ko in sorted(ENGLISH_LEAK_DICT.items(), key=lambda x: -len(x[0])):
        text = safe_replace(text, re.escape(en), ko)
    for hz, ko in sorted(HANJA_LEAK_DICT.items(), key=lambda x: -len(x[0])):
        text = safe_replace_hanja(text, hz, ko)
    return text


def call_exaone_word(word: str, context: str, timeout: float = 5.0) -> Optional[str]:
    """EXAONE에 단어 하나만 물어봄. 실패하면 None"""
    system = ("너는 한국어 번역가다. 주어진 문장의 지정 단어를 자연스러운 한국어로 바꾼 단어만 출력해. "
              "설명·따옴표 X. 5글자 이내.")
    user = f"문장: {context}\n\n위 문장의 \"{word}\"를 자연스러운 한국어 단어로?"
    req = {
        'model': REFINE_MODEL,
        'messages': [{'role': 'system', 'content': system}, {'role': 'user', 'content': user}],
        'stream': False, 'think': False,
        'options': {'temperature': 0.1, 'num_predict': 30, 'num_ctx': 1024, 'top_p': 0.7},
    }
    try:
        r = subprocess.run(['curl', '-s', '-X', 'POST', OLLAMA_URL,
                            '-H', 'Content-Type: application/json',
                            '-d', json.dumps(req)],
                           capture_output=True, text=True, timeout=timeout)
        out = json.loads(r.stdout).get('message', {}).get('content', '').strip()
        out = out.split('\n')[0].strip('"\'「」`* []()')
        m = re.search(r'[가-힣]+', out)
        return m.group(0) if m else None
    except Exception as e:
        logger.warning(f"EXAONE 단어 치환 실패 '{word}': {e}")
        return None


def llm_replace(text: str) -> str:
    """사전에 없는 누설 단어를 EXAONE으로 치환, 실패하면 제거"""
    english, hanja = detect_leaks(text)
    for word in english + hanja:
        idx = text.find(word)
        if idx < 0:
            continue
        ctx = text[max(0, idx-40):idx+len(word)+40]
        new_word = call_exaone_word(word, ctx)
        if new_word and new_word != word:
            if word in HANJA_LEAK_DICT or not word.isascii():
                text = safe_replace_hanja(text, word, new_word)
            else:
                text = safe_replace(text, re.escape(word), new_word, ignore_case=False)
            logger.info(f"[refiner] LLM 치환: '{word}' → '{new_word}'")
        else:
            text = text.replace(word, '', 1)
            logger.warning(f"[refiner] LLM 치환 실패, 강제 제거: '{word}'")
    return text


DANGSHIN_MAP = {
    '당신은': '너는',
    '당신을': '너를',
    '당신의': '너의',
    '당신이': '네가',
    '당신에게': '너한테',
    '당신께': '너한테',
    '당신과': '너와',
    '당신도': '너도',
    '당신만': '너만',
    '당신께서': '네가',
    '당신': '너',
}


def replace_dangshin(text: str) -> str:
    """'당신'을 반말 톤 '너/네'로 치환 (조사 포함 키부터)"""
    for k in sorted(DANGSHIN_MAP, key=len, reverse=True):
        text = text.replace(k, DANGSHIN_MAP[k])
    return text


def fix_mbti_typo(text: str) -> str:
    """모델이 가끔 내는 'MBTl'/'MBTL'/'MBT1' 오타를 'MBTI'로 정정"""
    return re.sub(r'MBT[lL1](?![a-zA-Z0-9_])', 'MBTI', text)


SYSTEM_TERM_PATTERNS = [
    (re.compile(r'(\d+단계에서\s*)', re.IGNORECASE), ''),
    (re.compile(r'(\d+단계가\s*)', re.IGNORECASE), '처음에 '),
    (re.compile(r'(\d+단계는\s*)', re.IGNORECASE), '그건 '),
    (re.compile(r'(\d+단계의\s*)', re.IGNORECASE), '앞의 '),
    (re.compile(r'(\d+단계\s*)', re.IGNORECASE), ''),
    (re.compile(r'(follow-?up\s*)', re.IGNORECASE), ''),
    (re.compile(r'(이어보기에서\s*)', re.IGNORECASE), ''),
    (re.compile(r'(CONTINUATION MODE\s*)', re.IGNORECASE), ''),
    (re.compile(r'(진단 모드|처방 모드)', re.IGNORECASE), '응답'),
]


def strip_system_terms(text: str) -> str:
    """시스템 프롬프트 내부 용어(예: '0단계에서')가 본문에 새어 나온 것 제거"""
    for pattern, replacement in SYSTEM_TERM_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


def fix_jondaemal_typical(text: str) -> str:
    """자주 나오는 존댓말을 반말로 치환. 1:1로 안전한 패턴만"""
    pairs = {
        '해드렸지만': '해줬는데',
        '해드렸어요': '해줬어',
        '해드렸어': '해줬어',
        '해드릴게요': '해줄게',
        '해드릴게': '해줄게',
        '해드릴': '해줄',
        '드릴게요': '줄게',
        '드릴게': '줄게',
        '말씀드리면': '말하자면',
        '말씀해': '말해',
        '해보세요': '해봐',
        '해주세요': '해줘',
    }
    for k, v in pairs.items():
        text = text.replace(k, v)
    return text


def remove_dup_paren(text: str) -> str:
    """영어 치환 후 생긴 중복 괄호 제거. 예: '컵 6 (컵 6)', '죽음(죽음)', '(탑) 탑'"""
    text = re.sub(r'([가-힣][가-힣\s\d]*?)\s*\(\s*\1\s*\)', r'\1', text)
    text = re.sub(r'\(\s*([가-힣][가-힣\s\d]*?)\s*\)\s+\1', r'\1', text)
    return text


def fix_broken_utf8(text: str) -> str:
    """모델이 한글을 <0xED><0x8E><0x90> 같은 바이트 토큰으로 내보낼 때 복원.
    복원 안 되면 해당 글자 제거"""
    def decode_seq(m):
        hexes = re.findall(r'<0x([0-9a-fA-F]{2})>', m.group(0))
        try:
            return bytes(int(h, 16) for h in hexes).decode('utf-8')
        except UnicodeDecodeError:
            return ''
    return re.sub(r'(?:<0x[0-9a-fA-F]{2}>)+', decode_seq, text)


def strip_html(text: str) -> str:
    """HTML 태그 전부 제거 (스트리밍 중 잘린 태그 포함)"""
    text = re.sub(r'<[a-zA-Z/][^<>]{0,200}>', '', text)
    text = re.sub(r'<[a-zA-Z/][^<>\n]{0,100}$', '', text, flags=re.MULTILINE)
    text = text.replace('&nbsp;', ' ').replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
    return text


def strip_markdown(text: str) -> str:
    """마크다운 굵게/기울임/코드 표시 제거"""
    text = re.sub(r'\*\*([^\*\n]+)\*\*', r'\1', text)
    text = re.sub(r'(?<!\*)\*([^\*\n]+)\*(?!\*)', r'\1', text)
    text = re.sub(r'`([^`\n]+)`', r'\1', text)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    return text


def strip_eng_in_parens(text: str) -> str:
    """한국어 옆 (English Name) 영어 괄호 제거. MBTI/AI 같은 SAFE 토큰만 보존"""
    def keep_safe(m):
        inner = m.group(1).strip()
        words = inner.split()
        if len(words) <= 2 and all(w.upper() in SAFE_ALPHA_TOKENS for w in words):
            return m.group(0)
        if re.fullmatch(r'[a-zA-Z][a-zA-Z\s]*', inner):
            return ''
        return m.group(0)
    return re.sub(r'\s*\(([^)]+)\)', keep_safe, text)


def refine(text: str) -> str:
    """정제 파이프라인. 규칙 기반 치환을 먼저 돌리고, 그래도 누설이 남으면 LLM 치환,
    그 뒤에도 남은 단어는 강제로 지움"""
    if not text:
        return text

    text = fix_mbti_typo(text)
    text = fix_broken_utf8(text)
    text = strip_html(text)
    text = strip_markdown(text)
    text = dict_replace(text)
    text = remove_dup_paren(text)
    text = strip_eng_in_parens(text)
    text = replace_dangshin(text)
    text = strip_system_terms(text)
    text = fix_jondaemal_typical(text)

    en, ha = detect_leaks(text)
    if en or ha:
        text = llm_replace(text)

        final_en, final_ha = detect_leaks(text)
        if final_en or final_ha:
            logger.warning(f"[refiner] 정제 후 잔존 — 강제 제거: 영어={final_en}, 한자={final_ha}")
            for w in final_en:
                text = re.sub(rf'(?<![a-zA-Z]){re.escape(w)}(?![a-zA-Z])', '', text)
            for w in final_ha:
                text = text.replace(w, '')

    text = fix_optional_yi_particle(text)
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r' +([,.!?])', r'\1', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text


def fix_broken_mbti_phrases(text: str) -> str:
    """MBTI 단어를 지운 뒤 남는 어색한 조각 정리.
    예: "INTP인 너라면"에서 INTP가 빠지면 "인 너라면"이 남음
    """
    # 문장 시작이나 쉼표/마침표 뒤의 "와 논리에" 같은 조각
    text = re.sub(r'([,.\n])\s*와\s+(논리|분석|이성|직관|감정)에\s+', r'\1 \2에 ', text)
    # 맨 앞에 온 경우
    text = re.sub(r'^\s*와\s+(논리|분석|이성|직관|감정)', r'\1', text)

    # 앞이 비어버린 "인 너라면", "한 너라면"
    text = re.sub(r'([,.\n])\s*인\s+너라면', r'\1 너라면', text)
    text = re.sub(r'([,.\n])\s*한\s+너라면', r'\1 너라면', text)
    # 문장 첫 부분
    text = re.sub(r'^\s*인\s+너라면', '너라면', text)
    text = re.sub(r'^\s*한\s+너라면', '너라면', text)

    text = re.sub(r'특히\s+인\s+너라면', '특히 너라면', text)
    text = re.sub(r'특히\s+한\s+너라면', '특히 너라면', text)

    # "특히 기질을 가진 너라면" 같은 추측성 표현은 여기서 못 고침. 프롬프트 쪽에서 막음

    return text


if __name__ == '__main__':
    samples = [
        "그들의轨迹를 쫓는 대신, 그 감정이 들끓는 순간을 기록해줘. 단순한 distraction이 아니야.",
        "너의 付出的 노력을 인정받고 싶은 마음, 이번 협상에선 冷静이 무기야.",
        "너의对你的 호감은 자연스러운 감정이야. 부담 없는 短信이나, Death 카드처럼 끝과 시작이 동시에.",
        "Five of Cups 카드가 나왔어. Wands의 흐름이 너에게 connection을 줄거야.",
        "그들의 connection은 깊어. observation이 핵심이지. 다른 distraction에 휘둘리지 마.",
    ]
    for s in samples:
        print(f"\n원본: {s}")
        result = refine(s)
        print(f"정제: {result}")
        en, ha = detect_leaks(result)
        print(f"누설 검사: 영어 {len(en)} 한자 {len(ha)}")
