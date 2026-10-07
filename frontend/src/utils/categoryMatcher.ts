/**
 * 사용자 질문을 광고 카테고리로 분류.
 * 백엔드 experts/router.py의 KEYWORD_MAP을 TS로 포팅.
 * 펫로스·가족상실 같은 sensitive 케이스도 감지 (광고 자제)
 */

type AdCategory = 'love' | 'family' | 'career' | 'money' | 'self' | 'daily'

const KEYWORD_MAP: Record<AdCategory, string[]> = {
  love: [
    '좋아', '짝사랑', '연애', '이별', '재회', '고백', '남친', '여친',
    '남자친구', '여자친구', '소개팅', '데이트', '결혼', '바람', '권태',
    '친구', '관계', '상대', '그 사람',
  ],
  family: [
    '엄마', '아빠', '엄빠', '부모', '부모님', '가족', '식구',
    '형제', '자매', '동생', '형', '오빠', '언니', '누나',
    '시어머니', '시아버지', '시댁', '처가', '장모', '장인',
    '남편', '아내', '와이프', '며느리', '사위',
    '아이', '아들', '딸', '자식',
  ],
  career: [
    '회사', '직장', '일', '업무', '이직', '취업', '면접', '입사',
    '퇴사', '사직', '창업', '사업', '승진', '평가', '연봉',
    '진로', '커리어', '직업', '적성', '번아웃', '워라밸',
    '학교', '학과', '전공', '자퇴', '휴학', '대학원',
  ],
  money: [
    '돈', '재물', '재정', '투자', '주식', '코인', '비트코인', '재테크',
    '저축', '예금', '적금', '빚', '대출', '카드값', '월급',
    '집', '부동산', '전세', '월세', '소비', '지출',
  ],
  self: [
    '자존감', '자아', '정체성', '의미', '가치관', '미래', '꿈', '목표',
    '우울', '불안', '무기력', '의욕', '행복', '삶', '인생',
    '뭘 원하는지', '왜 사는지', '나는 누구', '내가 누구',
  ],
  daily: [
    '오늘', '내일', '이번 주', '이번 달', '운세', '주말', '여행', '시험', '약속',
  ],
}

// 펫로스·가족상실: 광고 자제
const SENSITIVE_KEYWORDS = [
  '무지개다리', '강아지가 죽', '고양이가 죽', '반려동물이 죽', '펫로스',
  '돌아가신', '돌아가셨', '장례', '49재',
  // 위기 키워드도 sensitive (이미 백엔드 처리지만 광고도 자제)
  '자살', '자해', '죽고 싶', '사라지고 싶', '안녕 인사', '살 가치',
]

/**
 * 질문 키워드로 광고 카테고리 결정. 매칭 없으면 'daily'
 */
export function matchAdCategory(question: string): AdCategory {
  if (!question) return 'daily'
  const q = question.toLowerCase()

  const scores: Record<AdCategory, number> = {
    love: 0, family: 0, career: 0, money: 0, self: 0, daily: 0,
  }

  for (const [cat, keywords] of Object.entries(KEYWORD_MAP) as [AdCategory, string[]][]) {
    for (const kw of keywords) {
      if (q.includes(kw)) {
        scores[cat] += 1
      }
    }
  }

  const maxScore = Math.max(...Object.values(scores))
  if (maxScore === 0) return 'daily'

  // 동점이면 우선순위대로 (가족 갈등이 더 무거운 주제라 family가 love보다 앞)
  const priority: AdCategory[] = ['family', 'love', 'self', 'career', 'money', 'daily']
  for (const cat of priority) {
    if (scores[cat] === maxScore) return cat
  }
  return 'daily'
}

/**
 * sensitive 케이스 감지 (펫로스·가족상실·위기, 광고 자제)
 */
export function isSensitiveQuestion(question: string): boolean {
  if (!question) return false
  const q = question.toLowerCase()
  return SENSITIVE_KEYWORDS.some(kw => q.includes(kw))
}
