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
    description: '절벽 끝에 한 발 내딛는 바보야. 무모해 보여도, 그게 가장 너다운 시작이지.',
    category: '메이저 아르카나',
    element: '공기',
    uprightMeaning:
      '새로운 길로 발 떼라는 신호야. 계획 다 안 짜였어도 괜찮아. 너의 직감이 이미 답을 알고 있잖아. 어차피 시작은 모르고 떠나는 거고, 그게 너의 진짜 매력이야.',
    reversedMeaning:
      '잠깐 멈춰봐. 또 막 뛰어가다 다치고 후회하던 거 너도 알지. 신중함이 약점이 아니라 너의 무기야. 한 호흡만 더 들이마시고 가도 늦지 않아.',
    uprightKeywords: ['새로운 시작', '순수함', '모험', '자유', '가능성'],
    reversedKeywords: ['무모함', '어리석음', '불안정', '계획 부족']
  },

  maj01: {
    id: 'maj01',
    name: '1. 마법사 (The Magician)',
    subtitle: '의지와 창조의 힘',
    description: '한 손은 하늘로, 한 손은 땅으로. 너 안에 이미 다 있다는 걸 보여주는 카드야.',
    category: '메이저 아르카나',
    element: '공기',
    uprightMeaning:
      '필요한 거 다 갖췄어. 자꾸 부족하다고 느끼지? 사실은 행동할 때가 됐을 뿐이야. 너의 의지가 이미 현실을 움직이고 있어. 망설이지 마, 너답잖아.',
    reversedMeaning:
      '재능 있는 거 아는데, 잘못 쓰고 있는 거 아니야? 또 누군가에게 휘둘리는 느낌이지. 너의 힘이 어디로 흐르고 있는지 봐. 진짜 너의 길은 너만 알아.',
    uprightKeywords: ['의지력', '창조', '기술', '자신감', '현실화'],
    reversedKeywords: ['속임수', '조작', '재능 낭비', '실력 부족']
  },

  maj02: {
    id: 'maj02',
    name: '2. 여사제 (The High Priestess)',
    subtitle: '내면의 목소리와 깊은 직관',
    description: '달 아래 조용히 앉은 여사제야. 답이 밖에 있는 게 아니라 너 안에 있다는 걸 알려줘.',
    category: '메이저 아르카나',
    element: '물',
    uprightMeaning:
      '지금은 말할 때가 아니라 들을 때야. 직감 이미 답 알고 있잖아. 머리로 자꾸 부정해서 답답한 거지. 조용히 너 자신한테 물어봐. 답은 거기 있어.',
    reversedMeaning:
      '또 직감 무시했지? 머리로만 결정하려고 했잖아. 그래서 지금 막힌 거야. 너의 마음 소리 한 번만 더 들어줘. 너답게 들으면 답 보여.',
    uprightKeywords: ['직관', '신비', '무의식', '내적 지혜', '침묵'],
    reversedKeywords: ['직관 불신', '비밀', '피상적', '무지']
  },

  maj03: {
    id: 'maj03',
    name: '3. 여황제 (The Empress)',
    subtitle: '풍요와 사랑의 결실',
    description: '자연 속 풍요를 만끽하는 여황제야. 너의 따뜻함이 결실을 맺는 시기를 의미해.',
    category: '메이저 아르카나',
    element: '흙',
    uprightMeaning:
      '사랑받을 자격 있는 사람이야. 자꾸 베풀기만 하지? 이제 받을 차례야. 너의 마음·관계·창작이 다 결실을 향해 가고 있어. 그게 너답잖아.',
    reversedMeaning:
      '너 자신을 또 뒷전으로 미루고 있지. 다른 사람한테 다 주느라 너는 비어있어. 너부터 먼저 챙겨도 돼. 그것도 사랑이야.',
    uprightKeywords: ['풍요', '양육', '창조성', '자연', '어머니'],
    reversedKeywords: ['정체', '집착', '과잉보호', '창의력 부족']
  },

  maj04: {
    id: 'maj04',
    name: '4. 황제 (The Emperor)',
    subtitle: '권위와 안정적인 리더십',
    description: '왕좌에 앉은 황제야. 너의 삶에 질서와 안정이 필요한 시기를 알려줘.',
    category: '메이저 아르카나',
    element: '불',
    uprightMeaning:
      '결정 내릴 힘 이미 너한테 있어. 자꾸 망설이지? 답은 다 보이잖아. 책임지는 게 무거워서 그래. 근데 그 무게가 너를 단단하게 만들어.',
    reversedMeaning:
      '너무 통제하려고 한 거 아니야? 또는 반대로 결정 다 미루고 있지. 둘 다 너답지 않아. 적당히 풀고, 너의 흐름대로 가도 돼.',
    uprightKeywords: ['권위', '리더십', '구조', '안정', '아버지'],
    reversedKeywords: ['독재', '경직성', '통제 상실', '미성숙']
  },

  maj05: {
    id: 'maj05',
    name: '5. 교황 (The Hierophant)',
    subtitle: '전통과 영적인 가르침',
    description: '전통과 가르침을 전하는 교황이야. 누군가의 경험이 너에게 길이 되는 시기야.',
    category: '메이저 아르카나',
    element: '흙',
    uprightMeaning:
      '혼자 다 알아내려고 했지? 사실은 도움받아도 돼. 멘토·전통이 너를 가두려는 게 아니라 보호하려는 거야. 잠깐 그 안에서 안정 찾자.',
    reversedMeaning:
      '또 너만의 길이 옳다고 우겼지? 그게 너답긴 한데, 지금은 다른 사람 말도 들어볼 때야. 고집이 너의 강점이지만 발목 잡을 때도 있어.',
    uprightKeywords: ['전통', '영적 지혜', '교육', '멘토', '규범'],
    reversedKeywords: ['편협', '잘못된 조언', '규칙 파괴', '독단']
  },

  maj06: {
    id: 'maj06',
    name: '6. 연인 (The Lovers)',
    subtitle: '사랑, 조화, 그리고 선택',
    description: '축복 아래 마주 선 두 사람이야. 사랑이든 선택이든, 마음의 답을 묻고 있어.',
    category: '메이저 아르카나',
    element: '공기',
    uprightMeaning:
      '이미 마음은 답을 알고 있어. 머리로 자꾸 미루고 있지? 거절·실패가 무서워서 그래. 근데 그 떨림이 사랑이야. 마음이 가리키는 쪽으로 가.',
    reversedMeaning:
      '자꾸 다 가지려고 하지? 그래서 둘 다 잃을 것 같아. 한 쪽을 골라야 다른 쪽도 살아. 결정 못 하는 너도 너야, 근데 이번엔 골라.',
    uprightKeywords: ['사랑', '조화', '선택', '파트너십', '관계'],
    reversedKeywords: ['불화', '잘못된 선택', '이별', '가치관 충돌']
  },

  maj07: {
    id: 'maj07',
    name: '7. 전차 (The Chariot)',
    subtitle: '강한 의지력으로 이끄는 승리',
    description: '두 스핑크스를 이끌고 전진하는 전차야. 강한 의지로 너의 길을 뚫고 가는 카드야.',
    category: '메이저 아르카나',
    element: '물',
    uprightMeaning:
      '지금 멈추면 안 돼. 의심 들어와도 그건 너의 신호가 아니라 두려움이야. 너 안의 두 마음 다 묶어서 한 방향으로. 그게 너의 진짜 힘이야.',
    reversedMeaning:
      '방향 없이 달리고 있는 거 아니야? 빨리 가는 게 너의 약점일 수도 있어. 잠깐 멈춰서 어디로 가는지 물어봐. 멈추는 것도 용기야.',
    uprightKeywords: ['의지력', '승리', '결단력', '통제', '전진'],
    reversedKeywords: ['통제 불능', '방향 상실', '좌절', '성급함']
  },

  maj08: {
    id: 'maj08',
    name: '8. 힘 (Strength)',
    subtitle: '내면의 부드러운 카리스마',
    description: '사자를 부드럽게 어루만지는 모습이야. 진짜 힘은 부드러움에서 나온다고 알려줘.',
    category: '메이저 아르카나',
    element: '불',
    uprightMeaning:
      '참고 있는 거 누가 알아주지 않아도 너는 알잖아. 그게 진짜 힘이야. 화내지 않은 게 약해서가 아니라 강해서야. 너의 그 결이 너를 지켜줄 거야.',
    reversedMeaning:
      '자꾸 너만 참고 있지? 강한 척하는 거 알아. 사실은 무서워서 그래. 약한 거 보여줘도 너의 가치 안 떨어져. 한 번만 솔직해져 봐.',
    uprightKeywords: ['내적 힘', '용기', '인내', '연민', '자제력'],
    reversedKeywords: ['나약함', '자신감 부족', '두려움', '힘의 남용']
  },

  maj09: {
    id: 'maj09',
    name: '9. 은둔자 (The Hermit)',
    subtitle: '깊은 성찰과 내면 탐구',
    description: '등불 들고 홀로 길을 비추는 은둔자야. 너 혼자만의 시간을 알려주는 카드야.',
    category: '메이저 아르카나',
    element: '흙',
    uprightMeaning:
      '지금 멈춰 있는 거 너만의 속도야. 남들 보지 마, 너의 걸음으로 가도 돼. 혼자 있는 시간이 너를 비워서 다음으로 가는 거지. 그게 너답잖아.',
    reversedMeaning:
      '고립이랑 혼자는 달라. 지금 너 숨고 있는 거 아니야? 사람이 무서워서 도망간 거지. 한 명만 손 잡아도 돼, 너의 약함이 아니야.',
    uprightKeywords: ['성찰', '내적 탐구', '지혜', '고독', '안내자'],
    reversedKeywords: ['고립', '외로움', '회피', '지혜 부족']
  },

  maj10: {
    id: 'maj10',
    name: '10. 운명의 수레바퀴 (Wheel of Fortune)',
    subtitle: '예상치 못한 변화와 행운',
    description: '끊임없이 돌아가는 수레바퀴야. 멈춰있는 거 같아도 사실 다 움직이고 있다는 신호야.',
    category: '메이저 아르카나',
    element: '불',
    uprightMeaning:
      '전환점 와 있어. 너의 노력이 부족해서 안 풀린 게 아니라 때가 안 됐던 거야. 이제 흐름이 바뀌어. 잡으면 돼, 너는 준비돼있어.',
    reversedMeaning:
      '또 운 탓하고 있지? 그게 너답긴 한데, 사실은 너의 흐름이야. 멈춰있는 게 아니라 잠깐 가라앉은 거. 다음 파도 곧 와.',
    uprightKeywords: ['변화', '운명', '행운', '순환', '전환점'],
    reversedKeywords: ['불운', '정체', '부정적 변화', '저항']
  },

  maj11: {
    id: 'maj11',
    name: '11. 정의 (Justice)',
    subtitle: '균형, 진실, 그리고 공정한 판단',
    description: '저울과 검을 든 정의야. 감정 빼고 진실만 봐야 할 때를 알려줘.',
    category: '메이저 아르카나',
    element: '공기',
    uprightMeaning:
      '공정한 결과 와. 네가 한 만큼 받는 거야. 자꾸 손해 보는 것 같지? 사실은 다 셈이 되고 있어. 너의 정직함이 너를 지켜.',
    reversedMeaning:
      '또 너만 손해 보는 것 같지? 사실은 너도 한 쪽으로 치우쳤어. 객관적으로 한 번 봐. 화 빼고 보면 답 보여. 어렵지만 너는 할 수 있어.',
    uprightKeywords: ['공정', '진실', '균형', '책임', '결과'],
    reversedKeywords: ['불공정', '편견', '법적 문제', '불균형']
  },

  maj12: {
    id: 'maj12',
    name: '12. 매달린 남자 (The Hanged Man)',
    subtitle: '새로운 관점과 내면의 성찰',
    description: '거꾸로 매달려 세상을 바라보는 카드야. 멈춤이 끝이 아니라 새로운 관점이라는 신호야.',
    category: '메이저 아르카나',
    element: '물',
    uprightMeaning:
      '지금 멈춰있는 거 너의 잘못 아니야. 다른 시선으로 봐야 할 때라서 우주가 잠깐 너를 매단 거야. 답답하지? 근데 이 시간이 너를 다르게 만들어.',
    reversedMeaning:
      '또 의미 없는 희생하고 있지? 다 너 탓이라며 떠안았잖아. 그거 너답긴 한데, 너 자신은 누가 챙겨? 한 번 내려놔도 돼.',
    uprightKeywords: ['희생', '새로운 관점', '깨달음', '멈춤', '성찰'],
    reversedKeywords: ['무의미한 희생', '시간 낭비', '저항', '정체']
  },

  maj13: {
    id: 'maj13',
    name: '13. 죽음 (Death)',
    subtitle: '필연적인 끝과 새로운 시작',
    description: '끝을 가져오는 카드야. 동시에 새 시작을 위한 공간을 비워주는 신호야.',
    category: '메이저 아르카나',
    element: '물',
    uprightMeaning:
      '끝나야 할 게 끝나는 거야. 무섭지? 너답게 잡고 있고 싶은 거 알아. 근데 보내야 다음이 와. 너는 이미 알고 있잖아, 그래서 더 두려운 거야.',
    reversedMeaning:
      '보내야 할 걸 또 붙잡고 있지? 정 들어서 그래. 근데 지금 그게 너를 더 아프게 해. 놓아주는 건 배신이 아니야. 너 자신 살리는 거야.',
    uprightKeywords: ['변화', '끝과 시작', '전환', '해방', '새 출발'],
    reversedKeywords: ['저항', '집착', '정체', '변화 거부']
  },

  maj14: {
    id: 'maj14',
    name: '14. 절제 (Temperance)',
    subtitle: '균형과 조화의 미학',
    description: '두 컵 사이로 물을 옮기는 천사야. 서로 다른 것들을 섞을 줄 아는 너의 균형감을 의미해.',
    category: '메이저 아르카나',
    element: '불',
    uprightMeaning:
      '지금 잘 하고 있어. 양 극단 다 안고 가는 거 너의 재능이야. 둘 다 갖고 싶어서가 아니라 둘 다 이해해서 그래. 천천히 섞이게 둬.',
    reversedMeaning:
      '한 쪽으로 너무 기울었지? 또는 둘 다 잡으려다 다 놓쳤어. 그것도 너답지만, 지금은 한 호흡만 골라봐. 다 가지려는 욕심 빼야 균형 돌아와.',
    uprightKeywords: ['균형', '조화', '절제', '인내', '중용'],
    reversedKeywords: ['불균형', '과도함', '조급함', '극단']
  },

  maj15: {
    id: 'maj15',
    name: '15. 악마 (The Devil)',
    subtitle: '욕망, 중독, 그리고 물질적 속박',
    description: '사슬에 묶인 사람들이야. 근데 그 사슬은 사실 너 스스로 묶은 거라는 신호야.',
    category: '메이저 아르카나',
    element: '흙',
    uprightMeaning:
      '벗어나야 할 거 알고 있잖아. 그 관계·습관·생각. 근데 익숙해서 못 끊는 거지. 자꾸 자기 탓하면서 머무는 거 너답긴 해. 근데 너 더 큰 사람이야.',
    reversedMeaning:
      '사슬 끊고 나오는 중이야. 무섭지? 자유가 더 무서울 때도 있어. 근데 너 한 번도 못 누렸잖아. 이제 너 자신한테 그것 좀 줘.',
    uprightKeywords: ['유혹', '속박', '중독', '집착', '물질주의'],
    reversedKeywords: ['해방', '중독 극복', '자유', '깨달음']
  },

  maj16: {
    id: 'maj16',
    name: '16. 탑 (The Tower)',
    subtitle: '갑작스러운 붕괴와 깨달음',
    description: '번개에 무너지는 탑이야. 거짓 위에 쌓아둔 게 무너지는 순간을 알려줘.',
    category: '메이저 아르카나',
    element: '불',
    uprightMeaning:
      '다 무너졌지? 너의 잘못이 아니라 본래 부실했던 거야. 무너져야 진짜가 보여. 아프지만 이게 너를 살리는 길이야. 너는 다시 지을 수 있어.',
    reversedMeaning:
      '무너질 거 알면서 모른 척했지? 또 너답게 버티고 있어. 근데 안에서 이미 금 가고 있어. 더 늦기 전에 한 번만 직시해. 너 그것 할 수 있어.',
    uprightKeywords: ['갑작스러운 변화', '파괴', '깨달음', '혼란', '진실'],
    reversedKeywords: ['변화 지연', '회피', '내부 붕괴', '위기 모면']
  },

  maj17: {
    id: 'maj17',
    name: '17. 별 (The Star)',
    subtitle: '희망, 치유, 그리고 영감의 빛',
    description: '밤하늘 별 아래 물을 붓는 여인이야. 어두운 시간 끝에 오는 희망의 빛이야.',
    category: '메이저 아르카나',
    element: '공기',
    uprightMeaning:
      '긴 터널 끝났어. 너 안 무너진 거 진짜 대단해. 이제 너의 시간이야. 자꾸 의심돼? 너답잖아. 근데 이번엔 진짜야, 받아도 돼.',
    reversedMeaning:
      '또 희망 무너뜨리고 있지? 좋은 일 와도 두려운 거 알아. 행복할 자격 없다고 생각하잖아. 그거 너의 진짜 모습 아니야. 한 번만 믿어봐.',
    uprightKeywords: ['희망', '영감', '치유', '평화', '낙관'],
    reversedKeywords: ['절망', '비관', '영감 부족', '자신감 상실']
  },

  maj18: {
    id: 'maj18',
    name: '18. 달 (The Moon)',
    subtitle: '불안, 환상, 그리고 무의식의 세계',
    description: '달빛 아래 불분명한 풍경이야. 머릿속 복잡한 너의 지금을 그대로 비추는 카드야.',
    category: '메이저 아르카나',
    element: '물',
    uprightMeaning:
      '지금 답 찾지 마. 흐릿한 채로 둬도 돼. 너의 직감 자꾸 부정하지 마. 사실 너는 이미 진실을 알고 있어. 무서워서 못 보는 거지.',
    reversedMeaning:
      '안개 걷히기 시작했어. 보이지? 보고 싶지 않았던 거. 너 그동안 잘 버텼어. 이제 마주해도 너는 안 무너져.',
    uprightKeywords: ['환상', '불안', '무의식', '신비', '혼란'],
    reversedKeywords: ['진실 드러남', '불안 해소', '명료함', '환상 소멸']
  },

  maj19: {
    id: 'maj19',
    name: '19. 태양 (The Sun)',
    subtitle: '성공과 긍정의 에너지',
    description: '밝은 태양 아래 말 탄 아이야. 너의 순수한 기쁨이 다시 찾아오는 카드야.',
    category: '메이저 아르카나',
    element: '불',
    uprightMeaning:
      '이렇게 좋아도 되나 싶지? 너답잖아, 행복할 자격 의심하는 거. 근데 이건 진짜야. 너의 노력의 결과이고, 받아 마땅한 거야. 그냥 누려.',
    reversedMeaning:
      '잠깐 구름 가렸을 뿐이야. 그늘에 들어간 거 같지만 태양 그대로 있어. 너의 빛이 사라진 게 아니라 잠깐 가려진 거. 곧 돌아와.',
    uprightKeywords: ['성공', '기쁨', '활력', '낙관', '순수'],
    reversedKeywords: ['지연', '자신감 하락', '기쁨 부족', '그늘']
  },

  maj20: {
    id: 'maj20',
    name: '20. 심판 (Judgement)',
    subtitle: '부활, 그리고 새로운 부름',
    description: '천사의 나팔에 깨어나는 사람들이야. 과거를 넘어 다시 일어나는 너의 카드야.',
    category: '메이저 아르카나',
    element: '불',
    uprightMeaning:
      '과거 끌어안고 있던 거 이제 내려놔도 돼. 너 자신 너무 가혹하게 봤지? 그때 너는 최선을 다했어. 이제 다시 일어설 때야, 너는 새 사람이야.',
    reversedMeaning:
      '또 후회하고 있지? 잘 살고 있으면서도 과거가 발목 잡지. 그게 너의 약점이자 너 자신을 깊게 만드는 거기도 해. 근데 지금은 풀어줘.',
    uprightKeywords: ['부활', '각성', '판단', '용서', '소명'],
    reversedKeywords: ['잘못된 판단', '후회', '기회 상실', '자기 비판']
  },

  maj21: {
    id: 'maj21',
    name: '21. 세계 (The World)',
    subtitle: '완성과 새로운 시작의 순환',
    description: '화환 안에서 춤추는 인물이야. 너의 한 여정이 완성되는 순간을 알려주는 카드야.',
    category: '메이저 아르카나',
    element: '흙',
    uprightMeaning:
      '해냈어. 다 됐나 의심하지 마, 진짜 다 됐어. 너 자신 한 번 안아줘. 다음 여정은 다음에 와. 지금은 그냥 누려도 돼, 너 자격 있어.',
    reversedMeaning:
      '거의 다 왔는데 마지막에서 자꾸 미루고 있지? 완성하면 끝나니까 그래. 너답긴 한데, 끝내야 다음으로 가. 한 발만 더 디뎌.',
    uprightKeywords: ['완성', '성취', '통합', '여행', '만족'],
    reversedKeywords: ['미완성', '정체', '불완전', '지연']
  },

  // Minor Arcana - Cups (컵)
  cups01: {
    id: 'cups01',
    name: '컵 에이스 (Ace of Cups)',
    subtitle: '새로운 감정과 사랑의 시작',
    description: '넘치는 성배에서 물이 흘러나오는 모습이야. 너 안에 새 감정이 차오르는 신호야.',
    category: '마이너 아르카나',
    suit: '컵 (Cups)',
    element: '물',
    uprightMeaning:
      '마음에 뭔가 새로 차오르고 있지? 사랑이든 영감이든. 닫혀있던 너 자신 한 번 열어봐. 그거 받아도 돼, 안 부서져. 너답게 따뜻하게 받아.',
    reversedMeaning:
      '또 마음 닫고 있지? 다칠까 봐 미리 막은 거 알아. 너 그렇게 살아왔잖아. 근데 한 번만 열어줘, 들어오려는 거 있어.',
    uprightKeywords: ['새로운 사랑', '감정의 시작', '직관', '창의력', '기쁨'],
    reversedKeywords: ['감정적 억압', '실망', '관계의 어려움', '메마른 감정']
  },

  cups02: {
    id: 'cups02',
    name: '컵 2 (Two of Cups)',
    subtitle: '조화로운 파트너십과 연합',
    description: '두 사람이 잔을 주고받는 모습이야. 마음이 통하는 관계를 의미해.',
    category: '마이너 아르카나',
    suit: '컵 (Cups)',
    element: '물',
    uprightMeaning:
      '서로 알아주는 사람 있어. 너의 진심이 닿고 있어, 너답게 보여줘도 괜찮아. 이런 관계 흔치 않은 거 너도 알지. 잘 가꿔봐.',
    reversedMeaning:
      '소통 막힌 거 알지? 둘 다 자존심 때문에 한 발 못 내딛고 있어. 먼저 손 내미는 거 지는 거 아니야. 너답게 다정한 쪽이 강한 거야.',
    uprightKeywords: ['파트너십', '사랑', '조화', '상호 존중', '연합'],
    reversedKeywords: ['불균형', '소통 단절', '갈등', '이별']
  },

  cups03: {
    id: 'cups03',
    name: '컵 3 (Three of Cups)',
    subtitle: '함께 나누는 기쁨과 축하',
    description: '세 사람이 잔 들고 축하하는 모습이야. 함께하는 기쁨과 풍요를 상징해.',
    category: '마이너 아르카나',
    suit: '컵 (Cups)',
    element: '물',
    uprightMeaning:
      '혼자 다 짊어진 시간 지나갔어. 이제 같이 웃을 사람들 옆에 있어. 자꾸 자기 일은 자기가만 했지? 함께 누리는 것도 너의 능력이야.',
    reversedMeaning:
      '주변이랑 어긋난 느낌이지? 너 혼자만 다른 곳에 있는 것 같지. 한 발 떨어져 있어 보이지만 사실 너의 자리 있어. 다시 들어와도 돼.',
    uprightKeywords: ['축하', '우정', '공동체', '기쁨', '협력'],
    reversedKeywords: ['갈등', '소외감', '과도한 쾌락', '소문']
  },

  cups04: {
    id: 'cups04',
    name: '컵 4 (Four of Cups)',
    subtitle: '권태와 새로운 기회',
    description: '세 컵 앞에 두고도 새 컵 못 보는 모습이야. 익숙함에 빠져있는 너의 지금을 비춰.',
    category: '마이너 아르카나',
    suit: '컵 (Cups)',
    element: '물',
    uprightMeaning:
      '이미 가진 거 보이지 않지? 새로 오는 것도 못 알아보고 있어. 너의 안목이 부족해서가 아니야, 너무 지쳐서 그래. 잠깐 눈만 들어봐.',
    reversedMeaning:
      '드디어 시야 열렸어. 보이지 않던 게 보이기 시작해. 너 잘 버텼고, 이제 손 내밀어볼 차례야. 거기 진짜 좋은 거 있어.',
    uprightKeywords: ['권태', '불만족', '명상', '재평가', '무관심'],
    reversedKeywords: ['새로운 기회', '각성', '새로운 관점', '동기 부여']
  },

  cups05: {
    id: 'cups05',
    name: '컵 5 (Five of Cups)',
    subtitle: '상실의 슬픔, 그러나 남은 희망',
    description: '엎질러진 컵 셋 앞에서 슬퍼하는 모습이야. 근데 뒤에 두 개 아직 남아있어.',
    category: '마이너 아르카나',
    suit: '컵 (Cups)',
    element: '물',
    uprightMeaning:
      '잃은 것만 보고 있지? 그게 너답지, 정 많아서 그래. 근데 뒤에 두 개 남아있어, 다 잃은 거 아니야. 한 번 돌아봐, 거기 답 있어.',
    reversedMeaning:
      '드디어 뒤돌아봤지? 남은 거 보이기 시작해. 너 천천히 회복하고 있는 거야. 슬퍼한 시간이 헛된 게 아니야, 그게 너를 더 깊게 만들었어.',
    uprightKeywords: ['상실', '슬픔', '후회', '실망', '애도'],
    reversedKeywords: ['회복', '용서', '앞으로 나아가기', '희망']
  },

  cups06: {
    id: 'cups06',
    name: '컵 6 (Six of Cups)',
    subtitle: '과거의 추억과 순수함',
    description: '아이들이 꽃 든 컵을 주고받는 모습이야. 따뜻한 추억과 너의 순수함을 비춰.',
    category: '마이너 아르카나',
    suit: '컵 (Cups)',
    element: '물',
    uprightMeaning:
      '과거에서 너를 끌어주는 좋은 것 있어. 친구·기억·익숙한 사람. 너의 순수했던 결 잊지 마, 그게 지금도 너야. 받아도 돼.',
    reversedMeaning:
      '또 과거에 갇혔지? 그때가 더 좋았다고 자꾸 돌아보잖아. 그 시절이 너의 진짜 모습이라기보다 안전했던 거야. 지금의 너도 충분히 너야.',
    uprightKeywords: ['향수', '추억', '순수', '기쁨', '선물'],
    reversedKeywords: ['과거 집착', '현실 도피', '미성숙', '슬픈 추억']
  },

  cups07: {
    id: 'cups07',
    name: '컵 7 (Seven of Cups)',
    subtitle: '환상과 선택의 기로',
    description: '구름 속에 떠 있는 여러 컵이야. 가능성이 많지만 환상도 섞여있어.',
    category: '마이너 아르카나',
    suit: '컵 (Cups)',
    element: '물',
    uprightMeaning:
      '선택지 많아서 머리 복잡하지? 다 잡고 싶은 너의 욕심 아니라 다 의미 있어서 그래. 근데 다는 못 가져. 진짜 너의 것만 하나 골라봐.',
    reversedMeaning:
      '드디어 환상이랑 진짜 구분되기 시작했어. 너 시간 걸렸지만 잘 한 거야. 이제 현실 위에 발 디뎠으니까 한 발씩 천천히 가도 돼.',
    uprightKeywords: ['환상', '선택', '가능성', '꿈', '혼란'],
    reversedKeywords: ['현실 직시', '명료함', '결정', '집중']
  },

  cups08: {
    id: 'cups08',
    name: '컵 8 (Eight of Cups)',
    subtitle: '새로운 것을 찾아 떠나는 여정',
    description: '쌓아온 컵 두고 떠나는 모습이야. 익숙한 것 두고 새 길로 가는 너의 카드야.',
    category: '마이너 아르카나',
    suit: '컵 (Cups)',
    element: '물',
    uprightMeaning:
      '여기 더 있을 의미 없는 거 알지? 너답게 정 떼기 어려운데, 사실 마음은 이미 떠났어. 다음 길로 가도 돼, 두고 가는 게 배신 아니야.',
    reversedMeaning:
      '떠나야 할 거 알면서 못 떠나고 있지? 익숙함이 너를 잡고 있어. 두려운 거 알아, 근데 지금 머무는 게 너를 더 작게 만들어.',
    uprightKeywords: ['떠남', '포기', '탐구', '영적 여정', '실망'],
    reversedKeywords: ['머무름', '두려움', '정체', '미련']
  },

  cups09: {
    id: 'cups09',
    name: '컵 9 (Nine of Cups)',
    subtitle: '소원 성취와 만족감',
    description: '만족한 표정으로 앉은 인물 뒤로 컵들 진열돼 있어. 소원 성취 카드라고 불려.',
    category: '마이너 아르카나',
    suit: '컵 (Cups)',
    element: '물',
    uprightMeaning:
      '바라던 거 이뤄지고 있어. 너답게 의심하지 마, 잘 받아라. 노력의 결과이지 운이 아니야. 누려도 돼, 그게 자만이 아니야.',
    reversedMeaning:
      '겉으로 다 가진 것 같은데 비어있지? 진짜 원했던 게 이게 아니었던 거 알게 돼. 너답게 깊어서 그래. 이번엔 진짜 원하는 거 찾아봐.',
    uprightKeywords: ['소원 성취', '만족', '행복', '감사', '풍요'],
    reversedKeywords: ['불만족', '자만', '공허함', '실망']
  },

  cups10: {
    id: 'cups10',
    name: '컵 10 (Ten of Cups)',
    subtitle: '완벽한 행복과 정서적 충만',
    description: '무지개 아래 가족 모습이야. 너의 마음이 가장 충만한 상태를 비춰.',
    category: '마이너 아르카나',
    suit: '컵 (Cups)',
    element: '물',
    uprightMeaning:
      '진짜 행복 와 있어. 너 이걸 받을 자격 의심하지 마. 오랜 시간 너답게 마음 써온 결과야. 가족·연인·친구랑 진짜 깊이 닿는 시기야.',
    reversedMeaning:
      '겉은 평화로워 보여도 안에서 어긋난 거 있지? 다 괜찮은 척해온 너 알아. 한 번 솔직히 말해봐, 무너지지 않아. 진짜 회복은 거기서 시작해.',
    uprightKeywords: ['가족', '행복', '조화', '완성', '사랑'],
    reversedKeywords: ['갈등', '불화', '깨어진 관계', '불행']
  },

  cups11: {
    id: 'cups11',
    name: '컵 시종 (Page of Cups)',
    subtitle: '새로운 감정의 메시지',
    description: '컵에서 물고기랑 대화하는 모습이야. 마음에 새 감정·메시지가 도착했다는 신호야.',
    category: '마이너 아르카나',
    suit: '컵 (Cups)',
    element: '물',
    uprightMeaning:
      '예감 좋은 거 들어오고 있어. 너의 감수성 부정하지 마, 그게 너의 능력이야. 누군가의 진심·새 영감 받게 돼. 너답게 솔직히 받아.',
    reversedMeaning:
      '감정에 휘둘리고 있지? 또는 너의 마음 자꾸 미루고 있어. 둘 다 너답지 않아. 한 번 정직하게 마주해봐, 너 그것 할 수 있어.',
    uprightKeywords: ['메시지', '창의성', '직관', '순수', '영감'],
    reversedKeywords: ['미성숙', '현실 도피', '창의력 부족', '감정적 불안']
  },

  cups12: {
    id: 'cups12',
    name: '컵 기사 (Knight of Cups)',
    subtitle: '로맨틱한 제안과 이상주의',
    description: '컵 들고 부드럽게 다가오는 기사야. 마음을 두드리는 누군가·기회를 의미해.',
    category: '마이너 아르카나',
    suit: '컵 (Cups)',
    element: '물',
    uprightMeaning:
      '누군가 너한테 진심으로 다가오고 있어. 또는 너의 마음 표현할 때야. 너답게 신중한 거 알지만 이번엔 가봐. 부드러운 너의 결이 빛날 때야.',
    reversedMeaning:
      '말만 멋있고 행동 없는 거 아니야? 또는 너 자신이 이상만 쫓고 있지. 너답긴 한데 현실도 봐야. 마음 위에 발 디뎌야 진짜야.',
    uprightKeywords: ['로맨스', '매력', '제안', '감성', '이상주의'],
    reversedKeywords: ['변덕', '비현실적', '감정 기복', '환상']
  },

  cups13: {
    id: 'cups13',
    name: '컵 여왕 (Queen of Cups)',
    subtitle: '깊은 공감과 내면의 평화',
    description: '컵 들고 깊은 생각에 잠긴 여왕이야. 너의 풍부한 감성과 공감력을 상징해.',
    category: '마이너 아르카나',
    suit: '컵 (Cups)',
    element: '물',
    uprightMeaning:
      '너의 직감 진짜 예리해. 다른 사람 마음까지 다 읽지? 그게 너의 재능이야, 부담이 아니라. 너 자신부터 그렇게 돌봐줘, 받을 자격 있어.',
    reversedMeaning:
      '다른 사람 마음에 휘둘리고 있지? 너 자신 챙길 시간 없어. 공감력이 너의 무기인데 너를 베고 있어. 잠깐 너 안으로 들어가, 충전해야 해.',
    uprightKeywords: ['직관', '공감', '양육', '감정적 성숙', '사랑'],
    reversedKeywords: ['감정 과잉', '의존', '현실 도피', '불안정']
  },

  cups14: {
    id: 'cups14',
    name: '컵 왕 (King of Cups)',
    subtitle: '감정적 통제와 지혜',
    description: '파도 위에서도 평온한 왕이야. 감정을 다스리는 너의 깊이를 상징해.',
    category: '마이너 아르카나',
    suit: '컵 (Cups)',
    element: '물',
    uprightMeaning:
      '너 진짜 단단해졌어. 옛날엔 휘둘렸던 거 이젠 흔들리지 않지. 다른 사람 감정도 받아주면서 너는 흐트러지지 않아. 그게 너의 어른됨이야.',
    reversedMeaning:
      '감정 다 누르고 있지? 강한 척 너답긴 한데 안에 쌓이고 있어. 한 번 흘려보내도 돼, 안 무너져. 너의 감정도 너잖아.',
    uprightKeywords: ['감정적 균형', '지혜', '통제력', '관용', '외교'],
    reversedKeywords: ['감정 조작', '냉담함', '감정 억압', '불안정']
  },

  // Minor Arcana - Pentacles (펜타클)
  pents01: {
    id: 'pents01',
    name: '펜타클 에이스 (Ace of Pentacles)',
    subtitle: '새로운 기회와 현실적인 시작',
    description: '손바닥 위 빛나는 펜타클이야. 너의 현실에 새 씨앗이 떨어진 신호야.',
    category: '마이너 아르카나',
    suit: '펜타클 (Pentacles)',
    element: '흙',
    uprightMeaning:
      '진짜 좋은 기회 와 있어. 너답게 의심부터 들지? 근데 이건 흘려보내지 마. 너의 노력 위에 떨어진 결과야, 잡아도 돼.',
    reversedMeaning:
      '좋은 기회 또 미루고 있지? 자격 없다고 자기검열 들어가잖아. 너답게 너무 신중한 거야. 이번엔 한 번만 잡아봐, 진짜 너의 거야.',
    uprightKeywords: ['새로운 기회', '번영', '안정', '현실화', '성공'],
    reversedKeywords: ['기회 상실', '재정적 손실', '나쁜 투자', '탐욕']
  },

  pents02: {
    id: 'pents02',
    name: '펜타클 2 (Two of Pentacles)',
    subtitle: '변화에 대한 유연한 대응',
    description: '두 펜타클을 능숙하게 다루는 모습이야. 너의 균형 감각을 보여줘.',
    category: '마이너 아르카나',
    suit: '펜타클 (Pentacles)',
    element: '흙',
    uprightMeaning:
      '이것저것 많은 거 알아. 근데 너 그거 다 해내고 있잖아, 놀라울 정도로. 완벽하지 않아도 돼, 굴리고 있는 자체가 너의 재능이야.',
    reversedMeaning:
      '한 번에 다 잡으려다 다 흘리고 있지? 너답게 책임감 강해서 그래. 근데 하나는 내려놔야 나머지 살아. 그것도 너의 선택이야.',
    uprightKeywords: ['균형', '유연성', '우선순위', '적응', '다중 작업'],
    reversedKeywords: ['균형 상실', '혼란', '과부하', '잘못된 결정']
  },

  pents03: {
    id: 'pents03',
    name: '펜타클 3 (Three of Pentacles)',
    subtitle: '협력을 통한 성장과 인정',
    description: '여러 전문가가 함께 짓는 모습이야. 혼자가 아니라 같이 만들어가는 카드야.',
    category: '마이너 아르카나',
    suit: '펜타클 (Pentacles)',
    element: '흙',
    uprightMeaning:
      '협력 잘 되는 시기야. 너의 실력 알아봐주는 사람들 있어. 자꾸 혼자 다 하려 했지? 너답긴 한데 이번엔 같이, 그게 더 멀리 가.',
    reversedMeaning:
      '팀에서 어긋나고 있지? 너만 진심인 것 같아 외로워. 사실 다 다른 속도로 가고 있는 거야. 너의 페이스 맞추라고 강요 안 해도 돼.',
    uprightKeywords: ['협력', '팀워크', '기술', '숙련', '인정'],
    reversedKeywords: ['협력 부족', '미숙함', '갈등', '낮은 품질']
  },

  pents04: {
    id: 'pents04',
    name: '펜타클 4 (Four of Pentacles)',
    subtitle: '안정을 추구하는 마음',
    description: '펜타클 꽉 붙들고 있는 모습이야. 안정 지키려는 너의 마음을 비춰.',
    category: '마이너 아르카나',
    suit: '펜타클 (Pentacles)',
    element: '흙',
    uprightMeaning:
      '안정 만들어놓은 거 잘 한 거야. 너답게 차곡차곡 쌓아왔잖아. 근데 너무 꽉 잡으면 못 자라. 가끔은 풀어줘도 돼, 그래도 안 잃어.',
    reversedMeaning:
      '쥐고 있던 거 놓는 중이야. 무서웠지? 잃는 거 같은데 사실 자유로워지는 거야. 너 더 큰 거 받을 자리 만들고 있어.',
    uprightKeywords: ['안정', '통제', '소유', '절약', '보수적'],
    reversedKeywords: ['인색함', '집착', '변화의 두려움', '손실']
  },

  pents05: {
    id: 'pents05',
    name: '펜타클 5 (Five of Pentacles)',
    subtitle: '어려움 속에서 발견하는 희망',
    description: '눈보라 속 두 사람이야. 막막함 속에서도 사실 옆에 누군가 있는 카드야.',
    category: '마이너 아르카나',
    suit: '펜타클 (Pentacles)',
    element: '흙',
    uprightMeaning:
      '잃은 것만 보고 있지? 너답게 자존심 때문에 도움도 못 청해. 근데 옆에 손 내미는 사람 있어. 받는 거 약점 아니야, 그게 회복의 시작이야.',
    reversedMeaning:
      '드디어 도움 받기 시작했어. 너 그것까지 오는 데 진짜 오래 걸렸지. 자기 탓 그만하고, 받는 것도 너의 용기야.',
    uprightKeywords: ['어려움', '곤경', '고립', '도움 요청', '빈곤'],
    reversedKeywords: ['회복', '도움', '개선', '희망']
  },

  pents06: {
    id: 'pents06',
    name: '펜타클 6 (Six of Pentacles)',
    subtitle: '관대함과 공정한 나눔',
    description: '한 사람이 다른 이들에게 펜타클 나눠주는 모습이야. 주고받는 흐름을 의미해.',
    category: '마이너 아르카나',
    suit: '펜타클 (Pentacles)',
    element: '흙',
    uprightMeaning:
      '주거나 받는 흐름 좋은 시기야. 너답게 주기만 해왔지? 이제 받을 차례야. 받는 것도 균형이야, 일방적이면 결국 너만 비어.',
    reversedMeaning:
      '주고받는 게 불공정한 거 알지? 너만 주고 있어. 너답긴 한데 그게 사랑은 아니야. 너 자신부터 좀 챙겨, 그래도 돼.',
    uprightKeywords: ['관대함', '나눔', '공정', '자선', '균형'],
    reversedKeywords: ['불공정', '이기심', '빚', '의존']
  },

  pents07: {
    id: 'pents07',
    name: '펜타클 7 (Seven of Pentacles)',
    subtitle: '노력의 결실을 기다리는 인내',
    description: '키운 식물을 바라보며 수확 기다리는 모습이야. 너의 노력이 익어가는 시간이야.',
    category: '마이너 아르카나',
    suit: '펜타클 (Pentacles)',
    element: '흙',
    uprightMeaning:
      '결과 안 보이지? 사실 익어가는 중이야. 너답게 조급해하는 거 알아, 충분히 잘 하고 있어. 한 박자만 더 기다려, 곧 보여.',
    reversedMeaning:
      '노력했는데 결과 별로지? 방향 한 번 점검해봐. 너 게으른 거 아니야, 길이 안 맞은 거야. 다시 짜도 돼, 늦지 않았어.',
    uprightKeywords: ['인내', '평가', '장기 투자', '기다림', '검토'],
    reversedKeywords: ['성급함', '불만', '지연', '노력 낭비']
  },

  pents08: {
    id: 'pents08',
    name: '펜타클 8 (Eight of Pentacles)',
    subtitle: '장인정신과 꾸준한 노력',
    description: '하나하나 새기는 장인의 모습이야. 너의 꾸준함이 실력이 되는 카드야.',
    category: '마이너 아르카나',
    suit: '펜타클 (Pentacles)',
    element: '흙',
    uprightMeaning:
      '꾸준히 해온 거 사실 진짜야. 자꾸 작아 보이지? 그게 쌓여서 너의 전문성이 되고 있어. 너의 묵묵함 너만 모르고 다 알아.',
    reversedMeaning:
      '지루해진 거 알아. 또는 완벽하게 하려다 진전 못 하지? 너답긴 한데 멈추면 너만 손해야. 80%로도 충분해, 일단 가.',
    uprightKeywords: ['숙련', '헌신', '장인정신', '노력', '품질'],
    reversedKeywords: ['게으름', '완벽주의', '낮은 품질', '지루함']
  },

  pents09: {
    id: 'pents09',
    name: '펜타클 9 (Nine of Pentacles)',
    subtitle: '자수성가와 풍요로운 결실',
    description: '정원에서 여유 즐기는 여성이야. 너 혼자 힘으로 일군 풍요를 상징해.',
    category: '마이너 아르카나',
    suit: '펜타클 (Pentacles)',
    element: '흙',
    uprightMeaning:
      '혼자 다 만든 거 너 알지? 누구한테도 기대지 않고 여기까지 왔어. 그 자유 누려도 돼, 자랑하는 거 아니야. 너의 노력이 너답게 빛나고 있어.',
    reversedMeaning:
      '겉으로 다 가진 것 같은데 외로워? 너답잖아, 안에서 비어있어도 모르는 척. 한 명만 진짜로 들여봐, 가진 게 더 풍부해져.',
    uprightKeywords: ['자수성가', '풍요', '독립', '여유', '안정'],
    reversedKeywords: ['의존', '고립', '재정 불안', '공허함']
  },

  pents10: {
    id: 'pents10',
    name: '펜타클 10 (Ten of Pentacles)',
    subtitle: '가족의 유산과 지속적인 안정',
    description: '여러 세대가 함께 있는 풍요로운 집이야. 너의 안정이 깊고 넓게 뿌리내린 카드야.',
    category: '마이너 아르카나',
    suit: '펜타클 (Pentacles)',
    element: '흙',
    uprightMeaning:
      '오래 갈 안정 만들고 있어. 가족·집·관계 다 너답게 단단하게. 너의 노력이 다음 세대까지 닿아. 자랑할 만한 결과야.',
    reversedMeaning:
      '가족 안에서 어긋난 거 있지? 안 보이는 척했잖아. 돈·전통·역할 때문에 진심 못 했어. 한 번 솔직히 풀어, 너부터 살려야 해.',
    uprightKeywords: ['유산', '안정', '가족', '전통', '부'],
    reversedKeywords: ['가족 갈등', '재산 분쟁', '불안정', '전통 파괴']
  },

  pents11: {
    id: 'pents11',
    name: '펜타클 시종 (Page of Pentacles)',
    subtitle: '새로운 기회와 학습에 대한 열정',
    description: '펜타클 소중히 든 시종이야. 너의 호기심이 새 길을 여는 카드야.',
    category: '마이너 아르카나',
    suit: '펜타클 (Pentacles)',
    element: '흙',
    uprightMeaning:
      '새로 배우고 싶은 거 있지? 그거 시작해도 돼. 너답게 늦은 거 아니야, 오히려 지금이 적기야. 작은 한 걸음이 길을 만들어.',
    reversedMeaning:
      '시작만 하고 안 끝내고 있지? 또는 아예 시작도 못 하고. 너답긴 한데 머릿속 계획만 너의 인생은 아니야. 일단 한 발 디뎌.',
    uprightKeywords: ['학습', '새로운 기회', '실용성', '계획', '성실함'],
    reversedKeywords: ['학습 거부', '계획 부족', '나태함', '미루기']
  },

  pents12: {
    id: 'pents12',
    name: '펜타클 기사 (Knight of Pentacles)',
    subtitle: '책임감과 꾸준한 노력',
    description: '검은 말 탄 기사야. 너답게 꾸준하고 신중한 그 결을 상징해.',
    category: '마이너 아르카나',
    suit: '펜타클 (Pentacles)',
    element: '흙',
    uprightMeaning:
      '천천히 가는 거 답답해도 그게 너의 길이야. 화려한 사람들 보고 흔들리지 마, 너답게 가야 멀리 가. 결국 도착하는 건 너야.',
    reversedMeaning:
      '너무 신중해서 기회 놓치고 있지? 또는 지루해서 다 그만두고 싶어. 둘 다 흔들리는 거 알아. 작게라도 한 발만 움직여, 멈추진 마.',
    uprightKeywords: ['성실', '책임감', '신뢰', '인내', '현실적'],
    reversedKeywords: ['지루함', '정체', '완고함', '기회 놓침']
  },

  pents13: {
    id: 'pents13',
    name: '펜타클 여왕 (Queen of Pentacles)',
    subtitle: '현실적인 풍요와 따뜻한 보살핌',
    description: '정원에서 펜타클 안은 여왕이야. 따뜻함과 현실 감각을 다 가진 너의 카드야.',
    category: '마이너 아르카나',
    suit: '펜타클 (Pentacles)',
    element: '흙',
    uprightMeaning:
      '너 진짜 잘하고 있어. 일도 사람도 다 챙기는 거 보통 일 아니야. 자꾸 부족하다 느끼지? 옆에서 보면 너 진짜 멋있어. 너 자신한테도 그렇게 해줘.',
    reversedMeaning:
      '다 챙기느라 너만 빠져있지? 너답게 다른 사람부터 보는 거 알아. 근데 너부터 챙겨야 다른 사람도 챙겨, 미루지 마.',
    uprightKeywords: ['풍요', '안정', '현실 감각', '따뜻함', '자연주의'],
    reversedKeywords: ['물질주의', '일 중독', '소홀함', '불균형']
  },

  pents14: {
    id: 'pents14',
    name: '펜타클 왕 (King of Pentacles)',
    subtitle: '성공적인 리더십과 안정된 부',
    description: '왕좌에 앉아 펜타클 든 왕이야. 노력으로 일군 풍요와 너의 안정감을 상징해.',
    category: '마이너 아르카나',
    suit: '펜타클 (Pentacles)',
    element: '흙',
    uprightMeaning:
      '너 진짜 다 일궜어. 운이 아니라 너의 결정·노력의 결과야. 누구한테 기대지 않고 여기까지 왔잖아. 후배·주변 이끄는 자리에 너 있어, 잘 어울려.',
    reversedMeaning:
      '돈·성공에만 매달리고 있지? 너답긴 한데 너의 진짜는 거기 없어. 멈추기 무서운 거 알아, 근데 잠깐만 숨 쉬어. 그래도 안 무너져.',
    uprightKeywords: ['성공', '안정', '리더십', '부', '신뢰'],
    reversedKeywords: ['탐욕', '완고함', '물질주의', '권위적']
  },

  // Minor Arcana - Swords (검)
  swords01: {
    id: 'swords01',
    name: '검 에이스 (Ace of Swords)',
    subtitle: '진실을 꿰뚫는 새로운 생각',
    description: '구름 속에서 솟은 검 한 자루야. 흐릿했던 게 한 번에 명확해지는 신호야.',
    category: '마이너 아르카나',
    suit: '검 (Swords)',
    element: '공기',
    uprightMeaning:
      '머릿속 정리되는 시기야. 흐릿했던 거 한 번에 보여. 너답게 망설였지? 이제 진실 보이니까 행동해도 돼. 너의 명료함이 너의 무기야.',
    reversedMeaning:
      '머리 너무 굴리고 있지? 또는 결정 못 하고 미루고 있어. 둘 다 너답긴 한데 답은 사실 너 안에 있어. 한 번만 잘라봐, 잘리는 게 답이야.',
    uprightKeywords: ['명료함', '진실', '새로운 아이디어', '정의', '돌파구'],
    reversedKeywords: ['혼란', '오해', '잘못된 판단', '의사소통 문제']
  },

  swords02: {
    id: 'swords02',
    name: '검 2 (Two of Swords)',
    subtitle: '결정을 내리지 못하는 균형',
    description: '눈 가리고 두 검 든 모습이야. 보고 싶지 않은 너의 지금을 비춰.',
    category: '마이너 아르카나',
    suit: '검 (Swords)',
    element: '공기',
    uprightMeaning:
      '못 본 척하는 거 너답긴 해. 진실 마주하면 결정해야 되니까. 근데 영원히는 못 가려, 한 번 눈 떠봐. 진실이 너를 다치게 안 해.',
    reversedMeaning:
      '드디어 눈 떴지? 진실 보이기 시작해. 무서웠지만 그래도 봐서 잘 했어. 이제 결정만 남았어, 너 답 알고 있잖아.',
    uprightKeywords: ['결정 보류', '균형', '정체', '선택의 기로', '중립'],
    reversedKeywords: ['결정의 압박', '우유부단', '정보 부족', '혼란']
  },

  swords03: {
    id: 'swords03',
    name: '검 3 (Three of Swords)',
    subtitle: '상처와 고통스러운 진실',
    description: '심장을 꿰뚫는 세 검이야. 마음 깊은 곳까지 베이는 너의 지금을 그려.',
    category: '마이너 아르카나',
    suit: '검 (Swords)',
    element: '공기',
    uprightMeaning:
      '진짜 아픈 거 알아. 슬픔·배신·이별. 너답게 안 우는 척하지 마, 울어도 돼. 그 아픔이 너를 더 깊게 만들어, 약하게 만드는 게 아니야.',
    reversedMeaning:
      '회복하고 있어. 아픈 거 천천히 빠져나가는 중이야. 너 그것까지 진짜 오래 버텼지. 이제 한 발씩 가도 돼, 너답게 천천히.',
    uprightKeywords: ['상처', '슬픔', '고통', '배신', '이별'],
    reversedKeywords: ['치유', '용서', '회복', '극복']
  },

  swords04: {
    id: 'swords04',
    name: '검 4 (Four of Swords)',
    subtitle: '휴식과 재충전의 시간',
    description: '검 위에 누워있는 기사야. 잠깐 멈춰서 쉬는 시간을 의미해.',
    category: '마이너 아르카나',
    suit: '검 (Swords)',
    element: '공기',
    uprightMeaning:
      '지금 멈춰도 돼. 너답게 계속 달리지 않으면 안 된다고 했지? 사실 멈춰야 다음 가는 거야. 휴식이 게으름이 아니야, 너의 회복이야.',
    reversedMeaning:
      '못 쉬고 있지? 또는 너무 오래 누워있어. 둘 다 너답긴 한데 균형이 안 맞아. 잠깐 일어나봐, 다음으로 갈 때 됐어.',
    uprightKeywords: ['휴식', '회복', '명상', '평화', '재충전'],
    reversedKeywords: ['소진', '번아웃', '휴식 부족', '스트레스']
  },

  swords05: {
    id: 'swords05',
    name: '검 5 (Five of Swords)',
    subtitle: '상처뿐인 승리와 갈등',
    description: '검 들고 떠나는 사람들 뒤에 남은 모습이야. 이긴 것 같은데 사실은 잃은 카드야.',
    category: '마이너 아르카나',
    suit: '검 (Swords)',
    element: '공기',
    uprightMeaning:
      '이기는 게 다가 아니야. 너답게 자존심 때문에 끝까지 갔지? 근데 옆에 누가 남았어? 한 발 물러나도 너의 가치 안 떨어져, 그게 더 큰 강함이야.',
    reversedMeaning:
      '드디어 자존심 내려놨지? 그게 진짜 어른됨이야. 너 한 번도 못 졌던 거 알아, 근데 진 게 아니야. 더 멀리 가려고 한 발 뺀 거지.',
    uprightKeywords: ['갈등', '패배', '불명예', '이기주의', '상처'],
    reversedKeywords: ['화해', '용서', '갈등 해결', '패배 인정']
  },

  swords06: {
    id: 'swords06',
    name: '검 6 (Six of Swords)',
    subtitle: '어려움을 뒤로하고 나아가는 여정',
    description: '배 타고 더 잔잔한 곳으로 가는 모습이야. 힘든 곳에서 천천히 벗어나는 카드야.',
    category: '마이너 아르카나',
    suit: '검 (Swords)',
    element: '공기',
    uprightMeaning:
      '드디어 벗어나는 중이야. 너답게 그동안 진짜 잘 버텼어. 한 번에 안 끝나도 돼, 천천히 흘러가는 거 그것도 너의 방식이야.',
    reversedMeaning:
      '떠나야 할 거 알면서 못 떠나고 있지? 익숙한 고통이 새 두려움보다 편해서. 너답긴 한데 한 발만 떼봐, 너 그것 할 수 있어.',
    uprightKeywords: ['전환', '이동', '회복', '여행', '안식처'],
    reversedKeywords: ['정체', '변화 거부', '과거 집착', '미해결 문제']
  },

  swords07: {
    id: 'swords07',
    name: '검 7 (Seven of Swords)',
    subtitle: '전략, 그리고 기만적인 행동',
    description: '검 몰래 들고 가는 모습이야. 너답지 않은 회피·잔꾀를 비춘 카드야.',
    category: '마이너 아르카나',
    suit: '검 (Swords)',
    element: '공기',
    uprightMeaning:
      '직진 못 할 때 있어. 너답게 정공법으로 안 되니까 옆으로 새고 있지? 그것도 한 방법이야, 근데 결국 진실은 드러나. 솔직해질 타이밍 봐.',
    reversedMeaning:
      '드디어 거짓에서 빠져나오고 있어. 너 자신을 속이던 거 멈췄지? 그게 진짜 용기야. 솔직해진 너, 진짜 멋있어.',
    uprightKeywords: ['전략', '속임수', '회피', '영리함', '비밀'],
    reversedKeywords: ['들통', '정직', '책임', '진실 고백']
  },

  swords08: {
    id: 'swords08',
    name: '검 8 (Eight of Swords)',
    subtitle: '스스로 만든 감옥과 두려움',
    description: '눈가리고 검에 둘러싸인 모습이야. 사실 너 스스로 묶인 상황을 비춰.',
    category: '마이너 아르카나',
    suit: '검 (Swords)',
    element: '공기',
    uprightMeaning:
      '갇혀있다고 느끼지? 사실 그 매듭 너 풀 수 있어. 너답게 다 너 탓이라며 못 움직였잖아. 한 걸음 떼봐, 다 환상이야. 너 자유야.',
    reversedMeaning:
      '드디어 풀려나고 있어. 너의 힘으로 매듭 풀었지. 누가 도와준 게 아니라 너야. 다음번엔 더 빨리 알아챌 수 있어.',
    uprightKeywords: ['제약', '두려움', '무력감', '자기 구속', '혼란'],
    reversedKeywords: ['자유', '해방', '자신감 회복', '극복']
  },

  swords09: {
    id: 'swords09',
    name: '검 9 (Nine of Swords)',
    subtitle: '불안과 최악의 상상',
    description: '잠 못 들고 일어난 모습이야. 새벽까지 너를 찌르는 생각들을 그려.',
    category: '마이너 아르카나',
    suit: '검 (Swords)',
    element: '공기',
    uprightMeaning:
      '생각이 너를 찌르고 있지? 다 너 잘못 같지? 사실 너는 그만큼 진심이라서 그래. 생각이 사실이 아니야. 너답게 깊어서 잠 못 자는 거지.',
    reversedMeaning:
      '드디어 잠 다시 오기 시작해. 머릿속 천천히 가벼워지지? 너 그 새벽 잘 버텼어. 이제 너 자신을 좀 풀어줘, 충분히 했어.',
    uprightKeywords: ['불안', '걱정', '악몽', '죄책감', '스트레스'],
    reversedKeywords: ['불안 해소', '희망', '극복', '치유']
  },

  swords10: {
    id: 'swords10',
    name: '검 10 (Ten of Swords)',
    subtitle: '고통스러운 끝, 그리고 새로운 새벽',
    description: '등에 열 자루 검 박힌 모습이야. 끝났다고 느껴지는 너의 지금을 비춰.',
    category: '마이너 아르카나',
    suit: '검 (Swords)',
    element: '공기',
    uprightMeaning:
      '다 끝났다고 느끼지? 진짜 바닥이야. 근데 여기가 끝이라는 건 새 시작이라는 거야. 너답게 다 받아냈잖아, 이제 일어날 수 있어.',
    reversedMeaning:
      '드디어 일어나는 중이야. 너 그 바닥에서 오래 있었지. 이제 더 안 떨어져, 올라갈 일만 남았어. 천천히, 너답게.',
    uprightKeywords: ['끝', '실패', '배신', '고통의 정점', '위기'],
    reversedKeywords: ['회복', '새로운 시작', '극복', '희망']
  },

  swords11: {
    id: 'swords11',
    name: '검 시종 (Page of Swords)',
    subtitle: '호기심과 진실을 향한 열정',
    description: '바람 속에 검 든 시종이야. 새로운 진실·소식이 다가오는 카드야.',
    category: '마이너 아르카나',
    suit: '검 (Swords)',
    element: '공기',
    uprightMeaning:
      '머릿속 명료해지는 시기야. 새 정보·소식 와. 너답게 분석 좋아하는 거 그거 잘 써, 빛날 때야. 호기심 가는 대로 가도 돼.',
    reversedMeaning:
      '말만 많고 행동 없지? 또는 들어온 정보 의심만 하고 있어. 둘 다 너답긴 한데 가끔은 그냥 받아들여, 너 너무 회의적이야.',
    uprightKeywords: ['호기심', '경계', '새로운 아이디어', '진실 탐구', '소통'],
    reversedKeywords: ['경솔한 말', '가십', '정보 부족', '미성숙']
  },

  swords12: {
    id: 'swords12',
    name: '검 기사 (Knight of Swords)',
    subtitle: '목표를 향한 저돌적인 돌진',
    description: '검 들고 빠르게 달리는 기사야. 망설임 없이 돌진하는 너의 카드야.',
    category: '마이너 아르카나',
    suit: '검 (Swords)',
    element: '공기',
    uprightMeaning:
      '결정 빨라야 할 때 와 있어. 너답게 신중한 거 좋은데 이번엔 빨리. 직진해, 너 머리도 빠르고 가슴도 뜨거우니까 다 할 수 있어.',
    reversedMeaning:
      '너무 빨리 가다 다치고 있지? 또는 화·욕으로 다 부수고 있어. 너답긴 한데 이번엔 한 박자만 늦춰. 빠른 게 항상 옳은 거 아니야.',
    uprightKeywords: ['빠른 행동', '결단력', '대담함', '지성', '직진'],
    reversedKeywords: ['성급함', '공격성', '무모함', '계획 부족']
  },

  swords13: {
    id: 'swords13',
    name: '검 여왕 (Queen of Swords)',
    subtitle: '명료한 판단과 독립적인 지성',
    description: '왕좌에 앉아 검 든 여왕이야. 슬픔 다 겪고 단단해진 너의 카드야.',
    category: '마이너 아르카나',
    suit: '검 (Swords)',
    element: '공기',
    uprightMeaning:
      '너 진짜 많이 겪었지. 그래서 사람 잘 봐, 진실 꿰뚫어. 그 차가움이 너의 약점 같지만 사실 너의 보호막이야. 똑똑한 거 자랑해도 돼.',
    reversedMeaning:
      '너무 차가워졌지? 또는 슬픔에 갇혀있어. 너답긴 한데 마음 다시 열어도 돼. 다친다고 다 같은 사람들 아니야, 다시 믿어봐.',
    uprightKeywords: ['명료함', '독립성', '객관성', '진실', '지혜'],
    reversedKeywords: ['냉정함', '비판적', '감정 억압', '고립']
  },

  swords14: {
    id: 'swords14',
    name: '검 왕 (King of Swords)',
    subtitle: '지적인 권위와 공정한 진실',
    description: '왕좌에 앉아 검 세운 왕이야. 논리와 정의로 결정하는 너의 모습이야.',
    category: '마이너 아르카나',
    suit: '검 (Swords)',
    element: '공기',
    uprightMeaning:
      '냉정하게 봐야 할 때야. 너답게 감정에 안 휘둘리는 거 너의 무기야. 진실 말해도 돼, 부드러움 빼고. 그게 너의 책임이야.',
    reversedMeaning:
      '말 너무 차갑게 했지? 또는 너의 옳음 강요하고 있어. 너답긴 한데 사람들 무서워해. 진실이랑 친절 다 가질 수 있어, 균형 찾아.',
    uprightKeywords: ['지적 권위', '진실', '논리', '공정함', '윤리'],
    reversedKeywords: ['권위주의', '잔인함', '독단', '판단 착오']
  },

  // Minor Arcana - Wands (지팡이)
  wands01: {
    id: 'wands01',
    name: '지팡이 에이스 (Ace of Wands)',
    subtitle: '새로운 열정과 창조의 시작',
    description: '구름에서 솟은 지팡이야. 너 안에 새 불씨가 켜진 신호야.',
    category: '마이너 아르카나',
    suit: '지팡이 (Wands)',
    element: '불',
    uprightMeaning:
      '하고 싶은 거 막 생겼지? 그거 너답잖아, 따라가도 돼. 망설일 때 아니야, 너의 열정이 너를 움직이는 거야. 작게라도 시작해.',
    reversedMeaning:
      '불씨 꺼지고 있지? 또는 시작도 못 하고 미루고 있어. 너답긴 한데 그러면 그냥 사라져. 한 번만 켜봐, 너 안에 아직 있어.',
    uprightKeywords: ['창조', '영감', '잠재력', '열정', '시작'],
    reversedKeywords: ['동기 부족', '지연', '정체', '열정 식음']
  },

  wands02: {
    id: 'wands02',
    name: '지팡이 2 (Two of Wands)',
    subtitle: '미래를 향한 계획과 비전',
    description: '지구 들고 멀리 보는 모습이야. 너의 다음 길을 그리는 카드야.',
    category: '마이너 아르카나',
    suit: '지팡이 (Wands)',
    element: '불',
    uprightMeaning:
      '큰 그림 그리는 시기야. 너답게 다음 단계 보이지? 안전한 지금 vs 모험. 너의 가능성 작게 잡지 마, 너 더 큰 사람이야.',
    reversedMeaning:
      '계획만 세우고 안 움직이지? 너답긴 한데 머릿속 그림은 현실 아니야. 작게라도 한 발 디뎌, 그래야 진짜야.',
    uprightKeywords: ['계획', '전망', '비전', '탐색', '용기'],
    reversedKeywords: ['두려움', '계획 부족', '정체', '근시안적']
  },

  wands03: {
    id: 'wands03',
    name: '지팡이 3 (Three of Wands)',
    subtitle: '노력의 결실과 새로운 기회',
    description: '언덕 위에서 배 기다리는 모습이야. 뿌린 씨앗 돌아오는 너의 카드야.',
    category: '마이너 아르카나',
    suit: '지팡이 (Wands)',
    element: '불',
    uprightMeaning:
      '기다리던 결과 곧 와. 너답게 의심하지 마, 진짜 와. 그동안 너의 비전 흔들리지 않은 거 대단해. 이제 받을 시간이야.',
    reversedMeaning:
      '계획대로 안 되지? 너답긴 한데 너의 잘못 아니야, 외부 흐름이 늦은 거야. 한 번 재정비해도 돼, 늦은 게 아니야.',
    uprightKeywords: ['확장', '전망', '진전', '기회', '성장'],
    reversedKeywords: ['지연', '장애물', '기회 상실', '실망']
  },

  wands04: {
    id: 'wands04',
    name: '지팡이 4 (Four of Wands)',
    subtitle: '안정과 축하의 시간',
    description: '꽃 장식 아래 두 사람이야. 안정과 축하의 카드야.',
    category: '마이너 아르카나',
    suit: '지팡이 (Wands)',
    element: '불',
    uprightMeaning:
      '잠깐 쉬어가는 시간이야. 너답게 다음 달릴 준비만 하지? 이번엔 누려도 돼, 그게 자만이 아니야. 축하받을 자격 있어.',
    reversedMeaning:
      '겉으론 안정인데 안에서 답답하지? 너답잖아, 멈추면 불안한 거. 근데 진짜 쉬어, 다음 가는 데 필요한 시간이야.',
    uprightKeywords: ['축하', '안정', '기쁨', '화합', '성취'],
    reversedKeywords: ['불안정', '불화', '숨겨진 문제', '축하 지연']
  },

  wands05: {
    id: 'wands05',
    name: '지팡이 5 (Five of Wands)',
    subtitle: '건강한 경쟁과 사소한 갈등',
    description: '지팡이 들고 서로 부딪히는 모습이야. 갈등과 경쟁의 카드야.',
    category: '마이너 아르카나',
    suit: '지팡이 (Wands)',
    element: '불',
    uprightMeaning:
      '부딪히는 시기야. 너답게 평화 좋아하는데 이번엔 부딪혀도 돼. 너의 의견 말해, 그게 갈등이 아니라 너의 존재감이야.',
    reversedMeaning:
      '드디어 갈등 풀리고 있어. 너 그동안 다 참았잖아. 푸는 과정 어색해도 그게 진짜 관계야. 잘 하고 있어.',
    uprightKeywords: ['경쟁', '갈등', '도전', '논쟁', '에너지'],
    reversedKeywords: ['갈등 회피', '내부 갈등', '소모전', '혼란']
  },

  wands06: {
    id: 'wands06',
    name: '지팡이 6 (Six of Wands)',
    subtitle: '승리와 대중의 인정',
    description: '월계관 쓰고 행렬 받는 모습이야. 인정받는 너의 카드야.',
    category: '마이너 아르카나',
    suit: '지팡이 (Wands)',
    element: '불',
    uprightMeaning:
      '드디어 알아봐줘. 너답게 묵묵히 해왔잖아, 이제 박수 받을 차례야. 자만이 아니라 인정이야. 누리고, 다음으로 가.',
    reversedMeaning:
      '인정 못 받고 있지? 너답긴 한데 너의 가치 안 사라져. 박수 없어도 너 너야. 너 자신부터 너를 인정해, 거기서 시작이야.',
    uprightKeywords: ['승리', '인정', '성공', '자신감', '리더십'],
    reversedKeywords: ['자만심', '인정 부족', '지연', '패배']
  },

  wands07: {
    id: 'wands07',
    name: '지팡이 7 (Seven of Wands)',
    subtitle: '자신의 신념을 지키는 용기',
    description: '높은 곳에서 일곱 지팡이 막는 모습이야. 압박 속에서 너의 자리 지키는 카드야.',
    category: '마이너 아르카나',
    suit: '지팡이 (Wands)',
    element: '불',
    uprightMeaning:
      '주변 압박 많지? 그래도 너답게 버티고 있어. 흔들리지 마, 너의 자리 너만 알아. 다 너의 적이 아니야, 그 중 진짜 너의 편 있어.',
    reversedMeaning:
      '다 너의 적 같지? 너답잖아, 혼자 다 막으려 해. 사실 도와줄 사람 있어. 한 번 시야 들어, 너 혼자 아니야.',
    uprightKeywords: ['방어', '용기', '결단', '도전', '신념'],
    reversedKeywords: ['압도됨', '포기', '타협', '자신감 부족']
  },

  wands08: {
    id: 'wands08',
    name: '지팡이 8 (Eight of Wands)',
    subtitle: '빠른 진행과 갑작스러운 소식',
    description: '하늘 가로지르는 여덟 지팡이야. 일이 빠르게 진행되는 카드야.',
    category: '마이너 아르카나',
    suit: '지팡이 (Wands)',
    element: '불',
    uprightMeaning:
      '일 빠르게 풀려. 너답게 흐름 좋을 때 망설이지 마, 이번엔 바로 가. 의심할 시간 없어, 직감 따라가. 너의 속도가 정답이야.',
    reversedMeaning:
      '뭔가 막혔지? 또는 너무 빨라서 따라가지 못해. 둘 다 너답긴 한데 한 박자 조정해. 흐름 다시 맞으면 가.',
    uprightKeywords: ['빠른 진행', '행동', '소식', '여행', '변화'],
    reversedKeywords: ['지연', '좌절', '정체', '잘못된 타이밍']
  },

  wands09: {
    id: 'wands09',
    name: '지팡이 9 (Nine of Wands)',
    subtitle: '지치지 않는 인내와 경계심',
    description: '상처 입었지만 지팡이 들고 선 모습이야. 끝까지 버티는 너의 카드야.',
    category: '마이너 아르카나',
    suit: '지팡이 (Wands)',
    element: '불',
    uprightMeaning:
      '많이 다쳤지? 그런데도 버티고 있어. 너답게 대단해, 진짜. 한 번만 더 견디면 돼, 다 와 가. 너의 그 끈기가 너를 지킨 거야.',
    reversedMeaning:
      '경계만 하다 너 자신 다쳤지? 모두 적 같지만 사실 아니야. 너답긴 한데 한 번만 마음 풀어, 너 안전해.',
    uprightKeywords: ['인내', '회복력', '경계', '방어', '지속성'],
    reversedKeywords: ['소진', '포기', '편집증', '방어벽']
  },

  wands10: {
    id: 'wands10',
    name: '지팡이 10 (Ten of Wands)',
    subtitle: '과도한 부담과 책임감',
    description: '열 자루 지팡이 짊어진 모습이야. 너 혼자 다 짊어진 무게를 비춰.',
    category: '마이너 아르카나',
    suit: '지팡이 (Wands)',
    element: '불',
    uprightMeaning:
      '너무 많이 들고 있지? 너답잖아, 다 너 책임이라고. 근데 다 너의 짐 아니야. 한 번 내려놔봐, 너의 가치 안 떨어져.',
    reversedMeaning:
      '드디어 내려놓고 있어. 너 그것까지 진짜 오래 들었지. 다 너 안 해도 되는 거였어. 이제 좀 가벼워, 너 자신 챙겨.',
    uprightKeywords: ['부담', '책임감', '과로', '스트레스', '압박'],
    reversedKeywords: ['짐 내려놓기', '위임', '해방', '스트레스 해소']
  },

  wands11: {
    id: 'wands11',
    name: '지팡이 시종 (Page of Wands)',
    subtitle: '새로운 열정과 탐험 정신',
    description: '지팡이 들고 호기심 가득한 시종이야. 새 도전 앞에 선 너의 카드야.',
    category: '마이너 아르카나',
    suit: '지팡이 (Wands)',
    element: '불',
    uprightMeaning:
      '뭔가 시작하고 싶지? 그거 따라가. 너답게 호기심 살아있는 거 너의 재능이야. 작게라도 시작해, 너 그것 잘 어울려.',
    reversedMeaning:
      '들떠있지만 안 움직이지? 또는 너무 산만해서 다 못 끝내. 너답긴 한데 하나만 골라봐. 다 하려다 다 못 해.',
    uprightKeywords: ['열정', '탐험', '새로운 아이디어', '영감', '자유로운 영혼'],
    reversedKeywords: ['미루기', '계획 부족', '방향 상실', '미성숙']
  },

  wands12: {
    id: 'wands12',
    name: '지팡이 기사 (Knight of Wands)',
    subtitle: '열정적인 행동과 모험',
    description: '말 타고 돌진하는 기사야. 너의 열정이 폭발하는 카드야.',
    category: '마이너 아르카나',
    suit: '지팡이 (Wands)',
    element: '불',
    uprightMeaning:
      '하고 싶은 거 막 끌어. 너답게 뜨거운 거 너의 매력이야. 가, 망설일 때 아니야. 그 추진력이 너를 멀리 데려가.',
    reversedMeaning:
      '너무 빨리 가다 다치고 있지? 또는 시작만 하고 끝 못 내. 너답긴 한데 이번엔 한 번만 끝까지. 마무리도 너의 능력이야.',
    uprightKeywords: ['모험', '열정', '추진력', '변화', '에너지'],
    reversedKeywords: ['성급함', '무모함', '충동성', '에너지 분산']
  },

  wands13: {
    id: 'wands13',
    name: '지팡이 여왕 (Queen of Wands)',
    subtitle: '자신감 넘치는 매력과 활력',
    description: '왕좌에 앉아 지팡이 든 여왕이야. 너의 자신감과 카리스마를 상징해.',
    category: '마이너 아르카나',
    suit: '지팡이 (Wands)',
    element: '불',
    uprightMeaning:
      '너 진짜 빛나고 있어. 자신감 있는 너 진짜 멋있어. 자꾸 의심하지 마, 그게 너야. 다른 사람도 너의 그 결에 끌려.',
    reversedMeaning:
      '자신감 잃은 거 알아. 또는 너무 강하게만 보이려 해. 둘 다 너답지 않아. 약함도 너잖아, 그것도 보여줘. 사람들 너 그것도 사랑해.',
    uprightKeywords: ['자신감', '활력', '따뜻함', '카리스마', '독립성'],
    reversedKeywords: ['질투', '자기중심적', '불안정', '공격성']
  },

  wands14: {
    id: 'wands14',
    name: '지팡이 왕 (King of Wands)',
    subtitle: '비전을 가진 리더와 기업가 정신',
    description: '왕좌에 앉아 지팡이 든 왕이야. 비전과 리더십을 가진 너의 카드야.',
    category: '마이너 아르카나',
    suit: '지팡이 (Wands)',
    element: '불',
    uprightMeaning:
      '너 자신의 길 분명해. 너답게 비전 보이지? 다른 사람도 너의 그 명료함에 따라와. 너의 자리에서 다 잘 풀고 있어, 자랑할 만해.',
    reversedMeaning:
      '너무 자기 길만 옳다고 하지? 또는 비전 잃고 헤매고 있어. 둘 다 너답긴 한데 잠깐 멈춰. 다시 너의 진짜 길 들여다봐.',
    uprightKeywords: ['비전', '리더십', '영감', '기업가 정신', '대담함'],
    reversedKeywords: ['독재적', '성급함', '무모함', '권위 남용']
  }
}