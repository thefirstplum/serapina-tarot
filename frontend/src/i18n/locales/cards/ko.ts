export interface CardData {
  id: string
  name: string
  subtitle: string
  description: string
  category: '메이저 아르카나' | '마이너 아르카나'
  suit?: string
  element?: string
  uprightMeaning: string
  reversedMeaning: string
  uprightKeywords: string[]
  reversedKeywords: string[]
}

export const cardDatabase: Record<string, CardData> = {
  // Major Arcana
  maj00: {
    id: 'maj00',
    name: '0. 바보 (The Fool)',
    subtitle: '순수한 열정으로 떠나는 새로운 여정',
    description: '절벽 끝에 서서 미지의 세계로 발을 내딛는 모습은, 무한한 가능성과 순수한 믿음을 상징해요.',
    category: '메이저 아르카나',
    element: '공기',
    uprightMeaning:
      '새로운 시작, 순수한 열정, 무한한 가능성을 의미해요. 과거의 경험에 얽매이지 않고, 마음이 이끄는 대로 새로운 모험을 시작할 때가 왔음을 알려주는 긍정적인 신호예요.',
    reversedMeaning:
      '계획 없는 무모한 도전이나, 현실을 고려하지 않는 어리석은 선택을 경고하고 있어요. 잠시 멈춰서 상황을 신중하게 점검해볼 필요가 있음을 알려줘요.',
    uprightKeywords: ['새로운 시작', '순수함', '모험', '자유', '가능성'],
    reversedKeywords: ['무모함', '어리석음', '불안정', '계획 부족']
  },

  maj01: {
    id: 'maj01',
    name: '1. 마법사 (The Magician)',
    subtitle: '의지와 창조의 힘',
    description: '한 손은 하늘로, 한 손은 땅으로 향하며 우주의 힘을 다루는 모습은, 당신의 의지와 창조력을 상징해요.',
    category: '메이저 아르카나',
    element: '공기',
    uprightMeaning:
      '당신에게는 목표를 현실로 만들 힘이 있어요. 필요한 모든 재능과 도구를 이미 갖추고 있으니, 자신감을 갖고 행동을 시작할 때입니다. 당신의 의지가 현실을 창조할 거예요.',
    reversedMeaning:
      '재능을 잘못 사용하고 있거나, 속임수나 조작에 휘말릴 수 있음을 암시해요. 자신의 능력을 과신하기보다, 진실된 길을 가고 있는지 점검해보세요.',
    uprightKeywords: ['의지력', '창조', '기술', '자신감', '현실화'],
    reversedKeywords: ['속임수', '조작', '재능 낭비', '실력 부족']
  },

  maj02: {
    id: 'maj02',
    name: '2. 여사제 (The High Priestess)',
    subtitle: '내면의 목소리와 깊은 직관',
    description: '달 아래 앉아 신비로운 지혜를 간직한 모습은, 내면의 목소리와 깊은 직관의 중요성을 알려줘요.',
    category: '메이저 아르카나',
    element: '물',
    uprightMeaning:
      '지금은 행동하기보다 내면의 목소리에 귀 기울여야 할 때예요. 당신의 직관이 표면 아래 숨겨진 진실을 꿰뚫어 보고 있어요. 조용히 명상하며 기다리는 지혜가 필요해요.',
    reversedMeaning:
      '내면의 목소리를 무시하고 있거나, 중요한 정보를 놓치고 있을 수 있어요. 겉으로 보이는 것에만 집중하기보다, 숨겨진 진실이 무엇인지 살펴보세요.',
    uprightKeywords: ['직관', '신비', '무의식', '내적 지혜', '침묵'],
    reversedKeywords: ['직관 불신', '비밀', '피상적', '무지']
  },

  maj03: {
    id: 'maj03',
    name: '3. 여황제 (The Empress)',
    subtitle: '풍요와 사랑의 결실',
    description: '자연 속에서 풍요로움을 만끽하는 어머니 같은 모습은, 창조와 사랑의 결실을 상징해요.',
    category: '메이저 아르카나',
    element: '흙',
    uprightMeaning:
      '사랑과 보살핌을 주고받으며 풍요로움을 누릴 시기예요. 창의적인 프로젝트나 관계가 결실을 맺고, 물질적, 감정적 안정을 찾게 될 것을 의미해요.',
    reversedMeaning:
      '창의력이 막히거나, 관계에서 과도한 집착이나 소유욕을 보일 수 있어요. 자신을 돌보는 것을 잊지 말고, 건강한 균형을 찾는 것이 중요해요.',
    uprightKeywords: ['풍요', '양육', '창조성', '자연', '어머니'],
    reversedKeywords: ['정체', '집착', '과잉보호', '창의력 부족']
  },

  maj04: {
    id: 'maj04',
    name: '4. 황제 (The Emperor)',
    subtitle: '권위와 안정적인 리더십',
    description: '왕좌에 앉아 권위와 안정을 나타내는 아버지 같은 모습은, 리더십과 질서의 중요성을 말해줘요.',
    category: '메이저 아르카나',
    element: '불',
    uprightMeaning:
      '당신의 삶에 질서와 안정을 가져올 때예요. 리더십을 발휘하고, 명확한 규칙과 계획으로 목표를 달성할 수 있는 힘이 있어요. 책임감 있는 행동이 성공을 이끌 거예요.',
    reversedMeaning:
      '지나치게 권위적이거나, 반대로 통제력을 잃고 미성숙한 모습을 보일 수 있어요. 경직된 생각에서 벗어나 유연한 태도를 가질 필요가 있음을 암시해요.',
    uprightKeywords: ['권위', '리더십', '구조', '안정', '아버지'],
    reversedKeywords: ['독재', '경직성', '통제 상실', '미성숙']
  },

  maj05: {
    id: 'maj05',
    name: '5. 교황 (The Hierophant)',
    subtitle: '전통과 영적인 가르침',
    description: '영적 지혜를 전하는 종교적 지도자의 모습은, 전통과 사회적 규범의 가치를 상징해요.',
    category: '메이저 아르카나',
    element: '흙',
    uprightMeaning:
      '전통적인 가치나 제도를 따르는 것이 도움이 될 시기예요. 신뢰할 수 있는 멘토나 스승에게서 중요한 가르침을 얻거나, 사회적 규범 안에서 안정을 찾을 수 있어요.',
    reversedMeaning:
      '낡은 규칙에 얽매여 있거나, 반대로 무모하게 전통을 무시하고 있을 수 있어요. 고정관념에서 벗어나 자신만의 신념을 찾아야 할 때임을 알려줘요.',
    uprightKeywords: ['전통', '영적 지혜', '교육', '멘토', '규범'],
    reversedKeywords: ['편협', '잘못된 조언', '규칙 파괴', '독단']
  },

  maj06: {
    id: 'maj06',
    name: '6. 연인 (The Lovers)',
    subtitle: '사랑, 조화, 그리고 선택',
    description: '천사의 축복 아래 두 사람이 함께 서 있는 모습은, 사랑과 관계의 중요성을 의미해요.',
    category: '메이저 아르카나',
    element: '공기',
    uprightMeaning:
      '깊은 사랑이나 조화로운 관계의 시작을 의미해요. 또한, 당신의 가치관에 따른 중요한 선택의 순간이 다가왔음을 알려주기도 합니다. 마음이 이끄는 길을 선택하세요.',
    reversedMeaning:
      '관계의 불화나 잘못된 선택을 암시해요. 파트너와의 가치관 충돌이 있거나, 중요한 결정 앞에서 우유부단한 태도를 보이고 있을 수 있어요.',
    uprightKeywords: ['사랑', '조화', '선택', '파트너십', '관계'],
    reversedKeywords: ['불화', '잘못된 선택', '이별', '가치관 충돌']
  },

  maj07: {
    id: 'maj07',
    name: '7. 전차 (The Chariot)',
    subtitle: '강한 의지력으로 이끄는 승리',
    description: '상반된 두 스핑크스를 이끌고 전진하는 모습은, 강한 의지력과 통제력을 통한 성공을 상징해요.',
    category: '메이저 아르카나',
    element: '물',
    uprightMeaning:
      '강력한 의지력과 자신감으로 목표를 향해 돌진할 때예요. 어려움이 있더라도, 당신은 그것을 극복하고 승리를 쟁취할 힘을 가지고 있어요. 망설이지 말고 전진하세요.',
    reversedMeaning:
      '목표를 향한 방향을 잃거나, 의지력이 부족해 장애물 앞에서 좌절하고 있을 수 있어요. 너무 성급하게 돌진하기보다, 잠시 멈춰 방향을 재설정할 필요가 있어요.',
    uprightKeywords: ['의지력', '승리', '결단력', '통제', '전진'],
    reversedKeywords: ['통제 불능', '방향 상실', '좌절', '성급함']
  },

  maj08: {
    id: 'maj08',
    name: '8. 힘 (Strength)',
    subtitle: '내면의 부드러운 카리스마',
    description: '사자를 부드럽게 어루만지는 여성의 모습은, 진정한 힘이 부드러움에서 나옴을 보여줘요.',
    category: '메이저 아르카나',
    element: '불',
    uprightMeaning:
      '물리적인 힘이 아닌, 내면의 용기와 인내, 그리고 부드러운 카리스마로 상황을 이끌어갈 때예요. 두려움을 극복하고, 당신 안의 잠재된 힘을 믿으세요.',
    reversedMeaning:
      '자신감을 잃고 두려움에 휩싸여 있거나, 반대로 힘을 잘못 사용하고 있을 수 있어요. 내면의 나약함을 마주하고, 진정한 용기를 찾아야 할 때예요.',
    uprightKeywords: ['내적 힘', '용기', '인내', '연민', '자제력'],
    reversedKeywords: ['나약함', '자신감 부족', '두려움', '힘의 남용']
  },

  maj09: {
    id: 'maj09',
    name: '9. 은둔자 (The Hermit)',
    subtitle: '깊은 성찰과 내면 탐구',
    description: '등불을 들고 홀로 길을 비추는 현자의 모습은, 내면의 지혜를 찾기 위한 여정을 상징해요.',
    category: '메이저 아르카나',
    element: '흙',
    uprightMeaning:
      '세상의 소음에서 벗어나, 조용히 자신의 내면을 들여다볼 시간이에요. 혼자만의 시간을 통해 깊은 깨달음과 삶의 방향을 찾게 될 거예요. 스스로를 믿고 나아가세요.',
    reversedMeaning:
      '지나치게 고립되어 외로움을 느끼거나, 반대로 성찰을 회피하고 있을 수 있어요. 잠시 멈춰 자신의 마음을 돌보는 시간이 필요함을 알려줘요.',
    uprightKeywords: ['성찰', '내적 탐구', '지혜', '고독', '안내자'],
    reversedKeywords: ['고립', '외로움', '회피', '지혜 부족']
  },

  maj10: {
    id: 'maj10',
    name: '10. 운명의 수레바퀴 (Wheel of Fortune)',
    subtitle: '예상치 못한 변화와 행운',
    description: '끊임없이 돌아가는 수레바퀴는, 누구도 피할 수 없는 삶의 변화와 순환을 의미해요.',
    category: '메이저 아르카나',
    element: '불',
    uprightMeaning:
      '당신의 삶에 긍정적인 전환점이 찾아왔어요. 예상치 못한 행운이나 기회가 생길 수 있으니, 변화의 흐름에 몸을 맡겨보세요. 모든 것은 결국 좋은 방향으로 흘러갈 거예요.',
    reversedMeaning:
      '계획에 없던 어려움이나 불운이 닥칠 수 있어요. 하지만 이 또한 지나가는 과정일 뿐이에요. 변화에 저항하기보다, 상황을 받아들이고 다음을 준비하는 지혜가 필요해요.',
    uprightKeywords: ['변화', '운명', '행운', '순환', '전환점'],
    reversedKeywords: ['불운', '정체', '부정적 변화', '저항']
  },

  maj11: {
    id: 'maj11',
    name: '11. 정의 (Justice)',
    subtitle: '균형, 진실, 그리고 공정한 판단',
    description: '한 손에는 저울, 다른 손에는 검을 든 모습은, 감정에 치우치지 않는 공정함을 상징해요.',
    category: '메이저 아르카나',
    element: '공기',
    uprightMeaning:
      '지금까지의 행동에 대한 공정한 결과를 마주할 때예요. 객관적이고 논리적인 판단이 필요한 시점이며, 진실이 밝혀지고 모든 것이 제자리를 찾게 될 거예요.',
    reversedMeaning:
      '불공정한 상황에 처하거나, 편견으로 인해 올바른 판단을 내리지 못하고 있을 수 있어요. 책임을 회피하지 말고, 진실을 마주할 용기가 필요해요.',
    uprightKeywords: ['공정', '진실', '균형', '책임', '결과'],
    reversedKeywords: ['불공정', '편견', '법적 문제', '불균형']
  },

  maj12: {
    id: 'maj12',
    name: '12. 매달린 남자 (The Hanged Man)',
    subtitle: '새로운 관점과 내면의 성찰',
    description: '거꾸로 매달려 세상을 바라보는 모습은, 기존의 시각을 뒤집는 새로운 깨달음을 의미해요.',
    category: '메이저 아르카나',
    element: '물',
    uprightMeaning:
      '잠시 멈춰서 다른 관점으로 상황을 바라볼 필요가 있어요. 지금의 희생이나 기다림이 결국 더 큰 깨달음과 새로운 길을 열어줄 거예요. 조급해하지 마세요.',
    reversedMeaning:
      '의미 없는 희생을 하고 있거나, 시간을 낭비하고 있을 수 있어요. 현재의 노력이 올바른 방향인지 점검하고, 상황을 받아들이는 용기가 필요해요.',
    uprightKeywords: ['희생', '새로운 관점', '깨달음', '멈춤', '성찰'],
    reversedKeywords: ['무의미한 희생', '시간 낭비', '저항', '정체']
  },

  maj13: {
    id: 'maj13',
    name: '13. 죽음 (Death)',
    subtitle: '필연적인 끝과 새로운 시작',
    description: '모든 것을 끝내는 죽음의 기사는, 동시에 새로운 시작을 위한 공간을 마련하는 존재예요.',
    category: '메이저 아르카나',
    element: '물',
    uprightMeaning:
      '하나의 문이 닫히고, 새로운 문이 열리는 중요한 전환기예요. 과거의 것을 떠나보내야 새로운 것을 얻을 수 있어요. 이 끝은 더 나은 시작을 위한 과정이에요.',
    reversedMeaning:
      '변화를 두려워하고 과거에 얽매여 있음을 의미해요. 끝을 받아들이지 못하면 새로운 시작도 할 수 없어요. 놓아줄 용기가 필요한 시점이에요.',
    uprightKeywords: ['변화', '끝과 시작', '전환', '해방', '새 출발'],
    reversedKeywords: ['저항', '집착', '정체', '변화 거부']
  },

  maj14: {
    id: 'maj14',
    name: '14. 절제 (Temperance)',
    subtitle: '균형과 조화의 미학',
    description: '두 컵 사이의 물을 옮기는 천사의 모습은, 서로 다른 것들을 조화롭게 섞는 능력을 상징해요.',
    category: '메이저 아르카나',
    element: '불',
    uprightMeaning:
      '마음의 평화와 안정을 찾고, 모든 것을 조화롭게 만들어가는 시기예요. 극단적인 감정이나 행동을 피하고, 인내심을 갖고 중용의 미덕을 발휘해야 해요.',
    reversedMeaning:
      '감정의 기복이 심하거나, 삶의 균형이 깨져있음을 의미해요. 너무 조급해하거나 한쪽으로 치우친 생각은 상황을 더 악화시킬 수 있어요.',
    uprightKeywords: ['균형', '조화', '절제', '인내', '중용'],
    reversedKeywords: ['불균형', '과도함', '조급함', '극단']
  },

  maj15: {
    id: 'maj15',
    name: '15. 악마 (The Devil)',
    subtitle: '욕망, 중독, 그리고 물질적 속박',
    description: '사슬에 묶여 있지만 스스로 벗어날 수 있는 두 사람의 모습은, 우리가 만든 속박을 의미해요.',
    category: '메이저 아르카나',
    element: '흙',
    uprightMeaning:
      '물질적인 욕망, 중독, 또는 부정적인 관계에 얽매여 있을 수 있어요. 하지만 그 사슬은 스스로 끊어낼 수 있음을 기억하세요. 무엇이 당신을 묶고 있는지 직시할 때예요.',
    reversedMeaning:
      '부정적인 습관이나 속박에서 벗어나 자유를 향해 나아가고 있음을 의미해요. 스스로를 옭아매던 것들로부터 해방될 용기를 얻게 될 거예요.',
    uprightKeywords: ['유혹', '속박', '중독', '집착', '물질주의'],
    reversedKeywords: ['해방', '중독 극복', '자유', '깨달음']
  },

  maj16: {
    id: 'maj16',
    name: '16. 탑 (The Tower)',
    subtitle: '갑작스러운 붕괴와 깨달음',
    description: '번개에 맞아 무너지는 탑은, 거짓된 믿음이나 구조가 무너지는 순간을 상징해요.',
    category: '메이저 아르카나',
    element: '불',
    uprightMeaning:
      '예상치 못한 충격적인 사건으로 인해 기존의 상황이 완전히 무너질 수 있어요. 고통스럽겠지만, 이 파괴는 진실을 마주하고 새로운 시작을 하기 위한 필수 과정이에요.',
    reversedMeaning:
      '피할 수 있었던 위기나, 변화를 두려워하여 문제를 외면하고 있음을 의미해요. 내부로부터 서서히 붕괴가 진행되고 있을 수 있으니, 더 늦기 전에 상황을 점검해야 해요.',
    uprightKeywords: ['갑작스러운 변화', '파괴', '깨달음', '혼란', '진실'],
    reversedKeywords: ['변화 지연', '회피', '내부 붕괴', '위기 모면']
  },

  maj17: {
    id: 'maj17',
    name: '17. 별 (The Star)',
    subtitle: '희망, 치유, 그리고 영감의 빛',
    description: '밤하늘의 별 아래 물을 붓는 여인의 모습은, 순수한 희망과 치유의 에너지를 상징해요.',
    category: '메이저 아르카나',
    element: '공기',
    uprightMeaning:
      '어려운 시기가 지나고, 희망과 긍정의 빛이 당신을 비추고 있어요. 마음의 상처가 치유되고, 미래에 대한 새로운 영감과 믿음을 얻게 될 거예요. 평화로운 시기예요.',
    reversedMeaning:
      '희망을 잃고 비관적인 생각에 빠져있을 수 있어요. 자신에 대한 믿음이 부족하고, 미래가 불확실하게 느껴질 수 있지만, 희망의 빛은 사라지지 않았음을 기억하세요.',
    uprightKeywords: ['희망', '영감', '치유', '평화', '낙관'],
    reversedKeywords: ['절망', '비관', '영감 부족', '자신감 상실']
  },

  maj18: {
    id: 'maj18',
    name: '18. 달 (The Moon)',
    subtitle: '불안, 환상, 그리고 무의식의 세계',
    description: '달빛 아래 모든 것이 불분명하게 보이는 풍경은, 불안과 환상, 그리고 숨겨진 무의식을 상징해요.',
    category: '메이저 아르카나',
    element: '물',
    uprightMeaning:
      '상황이 명확하지 않고, 불안과 두려움이 커지는 시기예요. 현실과 환상을 구분하기 어려울 수 있어요. 지금은 당신의 직감과 꿈이 중요한 단서가 될 수 있어요.',
    reversedMeaning:
      '혼란스러웠던 상황이 점차 명확해지고, 숨겨진 진실이 드러나기 시작해요. 불안감에서 벗어나 현실을 직시하고, 올바른 판단을 내릴 수 있게 될 거예요.',
    uprightKeywords: ['환상', '불안', '무의식', '신비', '혼란'],
    reversedKeywords: ['진실 드러남', '불안 해소', '명료함', '환상 소멸']
  }
}