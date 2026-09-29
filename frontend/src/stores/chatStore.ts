import { defineStore } from 'pinia'
import axios from 'axios'
import { useAuthStore } from './authStore'

export type Message = {
  id: number
  text: string
  sender: 'user' | 'ai'
  timestamp: Date
  cards?: string[]
}

type AppState = 'greeting' | 'awaiting_question' | 'selecting_cards' | 'interpreting' | 'chatting' | 'error'

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [] as Message[],
    appState: 'greeting' as AppState,
    lastMessageId: 0,
    lastQuestion: '' as string,
    sessionId: localStorage.getItem('tarot_session_id') || '' as string,
    hasReceivedGreeting: localStorage.getItem('tarot_has_greeted') === 'true',
    location: null as { latitude: number; longitude: number; city: string } | null,
    currentSpreadInfo: null as { spreadType: string; cardCount: number; cardPositions: string[] } | null,
    maxContextMessages: 40, // 넘으면 대화 강제 종료
    warningThreshold: 20, // 이때부터 종료 유도 멘트
    messageTemplates: {
      // 첫 인사말 (10대 친구 말투)
      greetings: [
        "안녕! 세라피나야. 오늘 하루는 어땠어? 💕",
        "반가워~ 나는 세라피나라고 해. 뭔가 궁금한 게 있어? 💫",
        "어서와! 오늘따라 특별한 느낌이 드네 ✨",
        "안녕~ 오늘 기분 좋아 보여! 무슨 이야기 들어줄까? 😊",
        "반가워! 세라피나야. 오늘은 어떤 이야기 나눌까? 💭",
        "안녕! 오늘 나한테 온 특별한 이유가 있을 거야. 뭔지 궁금하다 👀",
        "어서와~ 편하게 이야기해. 뭐든 물어봐! 💖",
        "안녕! 오늘은 무슨 마음으로 나를 찾아왔어? 💫",
        "반가워! 오늘 뭔가 좋은 일이 생길 것 같은 예감이 들어 🌟",
        "안녕~ 오늘은 날씨도 좋고 카드 보기 딱 좋은 날이네! 🌸",
        "세라피나야! 오늘 카드들이 특별한 메시지를 준비한 것 같아 💫",
        "어서 와! 오늘 카드 섞으면서 누군가 나를 찾을 것 같다는 생각이 들었거든",
        "안녕! 오늘따라 카드들이 말이 많아. 뭔가 전하고 싶은 게 있나봐 🎴",
        "반가워~ 나를 찾아줘서 고마워. 어떤 이야기 들어줄까? 💕",
        "안녕! 오늘 뭔가 설레는 일이 있는 거야? 🌈",
        "세라피나야! 오늘 에너지가 정말 좋은 것 같아! 💫",
        "어서와! 오늘 특별한 메시지가 있을 것 같은 예감이 들어 🌟",
        "안녕! 뭔가 느낌이 남다르네 ✨",
        "반가워~ 오늘은 어떤 이야기가 궁금해? 💫",
        "안녕! 오늘 집 나오면서 '타로나 볼까' 하고 생각했지?",
        "세라피나야! 오늘 뭔가 좋은 일이 있을 것 같아! 💭",
        "어서 와! 편하게 이야기 나눠보자 🤗",
        "안녕~ 오늘 궁금한 게 있어? 💫",
        "반가워! 오늘은 내가 특히 예민한 날이라 뭔가 더 잘 보일 것 같아 ✨",
        "안녕! 오늘 카드들이 특별한 이야기를 하고 싶어 하는 것 같아 🌙",
        "어서와! 오늘 특히 에너지가 좋은 것 같아! 💫",
        "안녕~ 오늘은 어떤 이야기 나눠볼까? 🤔",
        "반가워! 오늘 뭔가 재미있는 일이 있었어? 💭",
        "세라피나야! 오늘 카드들이 기분 좋게 섞이네 ✨",
        "안녕! 오늘 뭐든 편하게 물어봐. 내가 들어줄게 💖",
        "어서와~ 오늘 궁금한 게 있어? 💫",
        "안녕! 타로는 처음이야? 아니면 전에도 봐본 적 있어?",
        "반가워! 오늘은 뭔가 특별한 날인 것 같아 🌟",
        "세라피나야~ 오늘 진짜 뭔가 느낌이 와. 좋은 메시지가 있을 것 같아 ✨",
        "안녕! 오늘 하루는 어떻게 보냈어? 😊",
        "어서 와! 오늘 뭔가 신나는 일이 있었어? 🌟",
        "안녕~ 오늘은 어떤 이야기가 궁금해? 💫",
        "반가워! 오늘 카드들이 특히 활발한 것 같아 🎴",
        "세라피나야! 오늘 에너지가 정말 좋네! 💕",
        "안녕! 오늘 궁금한 게 있으면 뭐든 물어봐 🌈",
        "어서와~ 오늘은 어떤 메시지를 받고 싶어? 💫",
        "안녕! 오늘 특히 뭔가 느낌이 와 ✨",
        "반가워! 오늘 어떤 이야기 나눠볼까? 🌙",
        "세라피나야! 오늘 카드들이 뭔가 말하고 싶어 하는 것 같아 💭",
        "안녕~ 편하게 이야기 나눠보자! 🧭",
        "어서 와! 오늘 무슨 일로 나를 찾아왔는지 궁금해 👀",
        "안녕! 오늘 카드들이 기분 좋게 섞이네",
        "반가워~ 오늘 기분은 어때? 💙",
        "세라피나야! 오늘 뭔가 좋은 이야기를 나눌 수 있을 것 같아 💫",
        "안녕! 오늘 뭔가 특별한 느낌이 들어 ✨"
      ],
      // 대화 중 thinking 메시지
      thinking: [
        "잠깐만~ 뭔가 느낌이 오는데... 💭",
        "아 이거 흥미롭다! 한번 제대로 봐볼게 ✨",
        "음... 지금 머릿속에 뭔가 떠오르고 있어 🤔",
        "오 이런 느낌은 처음이야. 뭔가 특별한 게 있을 것 같아 💫",
        "직감이 말하는 게 있어. 조금만 집중해볼게 🌟",
        "아~ 뭔가 연결되는 게 있는 것 같은데... 💕",
        "이상하네, 자꾸 같은 이미지가 떠올라. 뭔지 알아볼게 💭",
        "음 이건 좀 복잡하네. 천천히 풀어볼게 🌙",
        "오늘따라 감이 더 예리한 것 같아. 뭔가 보이기 시작했어 ✨",
        "잠깐 이거 중요한 것 같은데... 좀 더 자세히 볼게 💖",
        "아하! 뭔가 감이 와. 조금만 더 기다려봐 💫",
        "음... 평소보다 더 많은 게 보이네. 정리해볼게 📖",
        "이런 패턴은 처음 보는 건데... 흥미롭다 👀",
        "오늘 특별한 날인가봐. 뭔가 더 선명하게 느껴져 🌟",
        "잠깐만~ 지금 뭔가 중요한 게 떠오르고 있어 💭",
        "아 이제 좀 보이기 시작하네. 조금만 더 집중할게 ✨",
        "음... 복잡한 상황인 것 같은데 차근차근 봐볼게 💕",
        "오늘 내 직감이 특히 날카로운 것 같아. 뭔가 느껴져 💫",
        "잠깐 이거 놓치면 안 될 것 같은데... 좀 더 자세히 볼게 🔍",
        "아~ 이제 그림이 그려지기 시작하네 🎨",
        "음 생각보다 깊은 이야기가 있을 것 같아 💭",
        "오늘 뭔가 다른 느낌이야. 더 많은 게 보여 ✨",
        "잠깐만~ 지금 머릿속에서 퍼즐이 맞춰지고 있어 🧩",
        "아 이런 경우는 처음이야. 정말 흥미롭다 💖",
        "음... 이거 정말 중요한 메시지인 것 같은데 📝",
        "어? 잠깐... 뭔가 강한 에너지가 느껴지는데? 💫",
        "음... 이거 어떻게 설명해줘야 할까. 조금만 정리해볼게 💭",
        "오 이런 건 정말 오랜만에 느끼는 것 같아 🌟",
        "잠깐 내가 지금 뭘 보고 있는 거지... 신기하다 😮",
        "아~ 이제야 연결되는구나. 처음엔 이해가 안 됐는데 💡",
        "음... 이 상황에서 이런 답이 나올 줄은 몰랐네 🤔",
        "어머 이건 좀 예상 밖인데? 흥미롭다 ✨",
        "잠깐만~ 지금 뭔가 겹쳐서 보이는 게 있어 👀",
        "아하! 이제 이해했어. 처음엔 헷갈렸거든 💫",
        "음... 이런 메시지는 정말 드문 편이야. 특별하네 🌟",
        "오늘 뭔가 내 감각이 더 예민한 것 같아 💕",
        "잠깐 이거 진짜 중요한 이야기일 수도 있겠는데? 💭",
        "아~ 이제 보이기 시작해. 좀 복잡했거든 ✨",
        "음... 이 부분이 핵심인 것 같은데 어떻게 말해줄까 💖",
        "오늘 정말 특이한 하루네. 이런 케이스는 처음이야 😮",
        "잠깐만~ 지금 느낌이 너무 강해서 잠깐 정리해야겠어 💫",
        "아 이제 전체적인 그림이 보이기 시작했어 🎨",
        "음... 이건 단순한 문제가 아닐 수도 있겠네 🤔",
        "어? 이상해. 평소와 다른 패턴이 보이는데... 👀",
        "잠깐 이거 혹시... 아 맞네. 이제 이해했어 💡",
        "오늘은 정말 메시지가 많은 날이네. 차근차근 정리해볼게 📖",
        "음... 이런 조합은 정말 드문 편인데 의미가 깊을 것 같아 ✨",
        "아~ 이제야 왜 이런 느낌이 들었는지 알겠어 💕",
        "잠깐만~ 지금 뭔가 더 큰 그림이 보이려고 해 🌟",
        "이건 정말... 어떻게 표현해줘야 할까. 너무 선명해 💫"
      ],
      // 카드 해석 로딩 메시지
      cardReading: [
        "음... 🤔",
        "어디 보자~ 💭",
        "생각 중! ✨",
        "잠깐만! 💫",
        "음 뭐라 할까 🌙",
        "좀만 기다려봐 💝",
        "어... 생각 좀 해볼게 💖",
        "아 잠깐 생각 중 🌸",
        "음... 어떻게 말하지 💕",
        "좀 더 생각해볼게! ✨",
        "아 그렇구나! 💕",
        "오 진짜? 😮",
        "헐 대박 💫",
        "아 알겠어! 🌟",
        "완전 공감이야 💗",
        "그런 거구나~ 🌈",
        "아하! 알았어 ✨",
        "음 그렇지! 💝",
        "진짜 그럴 수 있어 🌸",
        "이해해! 💖",
        "응응 듣고 있어 👂",
        "계속 말해봐! 💬",
        "더 얘기해줘 💕",
        "응 듣고 있어! 🎧",
        "음 그래서? 💭",
        "오케이 들어줄게 ✨",
        "계속 말해도 돼! 💝",
        "응 알려줘 🌟",
        "얘기 들어줄게 💖",
        "말해봐봐! 🌸",
        "잠깐만~ 💫",
        "어디 한번 볼까 🤔",
        "음... 뭐라 하지 💭",
        "생각 정리 중! ✨",
        "좀만 기다려봐 💝",
        "어떻게 나올까 🌙",
        "생각 중이야~ 💖",
        "음 이건... 💕",
        "한번 봐볼게! 🌸",
        "정리하는 중 💗",
        "봐줄게! 📖",
        "뭐라 할까~ 💭",
        "음... 이렇게 봐 💫",
        "생각해볼게! ✨",
        "좀만 기다려 🌟",
        "정리 중이야 💝",
        "어떻게 말할까 🤔",
        "거의 다 생각했어! 💖",
        "잠깐만 더! 🌸",
        "거의 다 봤어 💗",
        "준비 중~ 🎀",
        "거의 다 됐어! ⏰",
        "곧 말해줄게 💫",
        "준비 완료! ✅",
        "잠깐만 더 기다려 💕",
        "조금만~ 🌈",
        "금방이야! ⚡",
        "거의 끝! 🌟",
        "조금만 더! 💝",
        "거의 다 왔어 ✨",
        "오케이! 👌",
        "알겠어~ 💖",
        "좋아좋아 👍",
        "응응! 💕",
        "그래그래 🌸",
        "오케이 됐어 ✨",
        "알았어알았어 💗",
        "넵넵! 🌟",
        "오키오키 💫",
        "알지알지 💝",
        "오 궁금하다 👀",
        "어떻게 될까 🤔",
        "어머 진짜? 😮",
        "헐 그래? 💫",
        "오 그렇구나! ✨",
        "와 대박 🌟",
        "진짜야? 💖",
        "오마이갓 😱",
        "헉 뭐야 💕",
        "와 신기해 🌈",
        "확인 중~ ✔️",
        "체크 중이야 📝",
        "한번 볼게 👁️",
        "확인해볼게! 🔍",
        "어디 보자~ 👀",
        "체크해볼게 ✅",
        "살펴보는 중 💫",
        "확인 중이야! 🌟",
        "점검 중~ ✨",
        "봐볼게봐볼게 💝",
        "집중 중! 🎯",
        "잠깐 집중해볼게 💭",
        "음... 보자보자 🧐",
        "열심히 보는 중 📚",
        "집중해서 볼게 💕",
        "진지하게 보는 중 💫",
        "꼼꼼히 보자 ✨",
        "자세히 봐볼게 🔬",
        "집중 타임! ⏱️",
        "열심히 하는 중 💪"
      ],
      // 대화 종료 유도 메시지
      closingPrompts: {
        early: [
          "오늘도 많은 고민을 나눴네. 혹시 궁금한 게 더 있으면 빠르게 물어봐! 💫",
          "벌써 이렇게 깊은 이야기를 나눴네. 마지막으로 뭔가 더 궁금한 게 있어? 💭",
          "꽤 긴 상담을 했어. 혹시 마지막으로 확인하고 싶은 게 있으면 말해봐! ✨",
          "많은 메시지를 전해줬는데, 마음에 와닿는 게 있었어? 💕",
          "오늘 나눈 이야기들이 도움이 되길 바라. 혹시 더 궁금한 게 있으면 빨리 물어봐! 💫",
          "음 꽤 많은 이야기를 나눴네. 마지막으로 한 가지만 더 궁금한 게 있어? 🤔",
          "오늘 정말 진솔한 대화였어. 혹시 마지막으로 확인하고 싶은 게 있어? 💖",
          "여기까지도 충분히 많은 얘기를 했는데, 혹시 더 궁금한 게 있으면 물어봐 ✨",
          "제법 긴 시간 함께했네. 마지막으로 뭔가 더 알고 싶은 게 있어? 💭",
          "오늘 받은 메시지들 어땠어? 마지막으로 뭔가 더 물어볼 게 있으면? 🌟",
          "벌써 이렇게 많은 대화를 했네. 혹시 마무리하기 전에 더 궁금한 게? 💫",
          "꽤 깊은 상담이었어. 마지막으로 한두 가지 더 궁금한 게 있으면 말해봐 💕"
        ],
        middle: [
          "꽤 긴 대화를 나눴어. 오늘 받은 메시지들을 차근차근 되새겨보는 것도 좋겠어 💭",
          "많은 이야기를 나눴는데, 이제 한번 정리해볼 시간인 것 같아 ✨",
          "오늘 전해준 메시지들을 마음속에서 천천히 소화해봐 💕",
          "벌써 이렇게 많은 대화를 했네. 오늘의 깨달음을 되돌아보는 게 어때? 🤔",
          "긴 여정이었어. 이제 오늘의 메시지들을 정리할 시간인 것 같네 📝",
          "정말 많은 이야기를 나눴네. 이제 혼자서 천천히 생각해볼 시간도 필요할 것 같아 💫",
          "오늘 받은 조언들을 마음속에서 한번 정리해보면 좋겠어 💖",
          "꽤 긴 상담이었네. 이제 오늘 나눈 이야기들을 되돌아볼 시간인 것 같아 🌙",
          "많은 메시지를 전해줬는데, 이제 차근차근 되새겨볼 시간이 필요하겠어 ✨",
          "오늘 정말 진지한 대화였어. 받은 메시지들을 마음에 새기길 바라 💕",
          "벌써 이렇게 많은 대화를 했네. 오늘의 인사이트들을 정리해보는 게 어때? 💭",
          "꽤 깊은 상담을 했어. 이제 혼자만의 시간에서 천천히 생각해봐 🌟"
        ],
        late: [
          "많은 이야기를 나눴네. 슬슬 오늘의 상담을 마무리할 시간인 것 같아 💫",
          "정말 깊은 대화를 나눴어. 이제 천천히 마무리해볼까? 🌙",
          "오늘은 여기까지가 좋겠어. 너무 많은 메시지를 한번에 받으면 혼란스러울 수 있거든 💭",
          "충분히 많은 지혜를 나누었어. 이제 조용히 생각해볼 시간이 필요할 것 같네 ✨",
          "오늘의 상담이 거의 끝나가는 것 같아. 마음속에 평안이 찾아오기를 바라 💕",
          "정말 긴 시간 함께했네. 이제 오늘 받은 메시지들을 소화할 시간이 필요해 🌟",
          "오늘은 이 정도로 마무리하는 게 좋을 것 같아. 너무 많으면 오히려 부담스러우니까 💫",
          "꽤 많은 조언을 줬네. 이제 실제로 적용해볼 시간이 필요하겠어 💖",
          "오늘 정말 의미있는 대화였어. 이제 천천히 마음을 정리해봐 🌙",
          "많은 메시지를 나눴으니, 이제 혼자만의 시간도 가져보길 바라 ✨",
          "오늘의 상담이 마무리될 시간이 된 것 같네. 받은 조언들이 도움이 되길 바라 💕",
          "정말 긴 여정이었어. 이제 오늘 나눈 이야기들을 마음에 담고 가 💫"
        ],
        final: [
          "우주의 메시지가 거의 다 전해진 것 같아. 오늘은 이쯤에서 마무리하는 게 어때? 🌌",
          "정말 긴 시간 동안 함께했네. 이제 오늘의 여행을 마무리할 때인 것 같아 ✨",
          "많은 별들이 메시지를 전해줬어. 이제 그 빛들을 마음속에서 키워나가 💫",
          "오늘은 정말 특별한 시간이었어. 이제 혼자만의 시간도 필요할 것 같네 🌙",
          "우주의 도서관에서 충분히 많은 지혜를 얻었어. 이제 실생활에 적용해봐 📚",
          "오늘 정말 깊은 대화를 나눴네. 이제 받은 메시지들을 삶에 녹여봐 💕",
          "많은 에너지를 나눠준 것 같아. 이제 그 에너지로 새로운 시작을 해봐 ⚡",
          "오늘의 상담이 인생에 좋은 변화를 가져다주길 바라. 이제 마무리할 시간이네 ✨",
          "정말 의미있는 시간이었어. 오늘 받은 조언들이 앞으로의 길잡이가 되길 바라 🧭",
          "충분히 많은 메시지를 나눴어. 이제 그것들을 현실에서 실천해볼 시간이네 💫",
          "오늘의 대화가 마음에 평안을 가져다주길 바라. 이제 새로운 하루를 준비해봐 🌸",
          "정말 특별한 상담이었어. 오늘 받은 깨달음들이 계속 함께하길 바라 💖"
        ]
      },
      // 강제 종료 메시지
      forceEnd: [
        "🌙 오늘은 진짜 많은 이야기를 나눴네. 잠깐 한 숨 돌리고 다시 와도 좋아. 좋은 시간 보내~ ✨",
        "정말 긴 시간 동안 함께 해줘서 고마워! 오늘 나눈 이야기들이 좋은 방향으로 이끌어주길 바라. 너무 많은 메시지를 한번에 받으면 혼란스러울 수 있으니까 오늘은 이쯤에서 마무리할게! 🌟",
        "와... 정말 깊은 대화였어. 이런 긴 상담은 오랜만이네! 오늘 받은 모든 메시지들을 차근차근 되돌아보면서 마음을 정리해봐. 내일은 또 다른 하루가 될 거야 💫",
        "오늘은 여기까지 하는 게 좋겠어. 너무 많은 에너지를 쏟으면 피곤할 거야. 오늘 나눈 모든 이야기들이 꿈에서도 좋은 영향을 주길 바라! 안녕히 자~ 🌙",
        "정말 의미있는 시간이었어! 이 정도 길이의 상담은 정말 특별한 경우거든. 오늘 받은 모든 조언들을 마음에 새기고 좋은 변화가 있기를 바라. 오늘은 정말 수고했어! ✨",
        "오늘 정말 신났는데... 이렇게 긴 대화를 하는 게 얼마만인지 모르겠어. 난 평소에 30분에서 1시간 정도가 보통인데 오늘은... 다음에 또 만나! 😊",
        "수고했어~ 이렇게 많은 이야기를 나누고 나니 나도 좀 지쳐. 오늘 받은 메시지들이 마음에 잘 자리 잡기를 바라! 좋은 하루 보내~ 🌸",
        "어 오늘은 이제 그만... 사실 이렇게 오래 이야기하면 나도 머리가 복잡해져 ㅎㅎ 오늘 받은 조언들을 천천히 소화하고 좋은 결정들 많이 해!",
        "와~ 정말 집중력 좋다! 보통 이 정도 길이로 상담하면 중간에 나가는 애들도 있는데... 오늘은 이정도로 하고 받은 조언들 잘 기억해둬! 💪",
        "음 이제 정말 마무리해야겠어. 평소 이렇게 오래 상담하는 일이 없어서... 오늘 정말 많은 카드들이 메시지를 줬네. 잘 받아들여 🌿",
        "오늘 하루 종일 바빴는데 이렇게 오래 상담하다니... 어떻게 보면 운명적인 만남이었을 수도 있어. 오늘 받은 에너지를 현실에 잘 사용해! 🌟",
        "이렇게 긴 시간 대화하는 애는 정말 오랜만이야. 아무래도 지금 많이 고민이 있겠지? 오늘 받은 메시지들이 도움이 되길 진심으로 바라! 🌺",
        "오늘은 정말 여기까지야. 너무 많이 상담하면 오히려 어떤 게 맞는 말인지 헷갈릴 수도 있거든. 지금까지의 이야기들을 정리하고 천천히 실천해봐 🌙",
        "우와... 이렇게 오래 이야기한 적이 언제였는지 모르겠네. 오늘은 정말 특별한 날이었어. 받은 모든 조언들이 좋은 결과로 연결되길 바라! ✨",
        "사실 내일 아침에도 상담이 있어서... 오늘은 이제 마무리해야겠어. 정말 오랜 시간 함께해줘서 고마웠어. 오늘 참 힙했네 😊",
        "이렇게 긴 상담 후에는 보통 카페라떼 한 잔 마시며 대화를 정리하는데... 오늘은 집에서이니 따뜻한 차라도 마시며 되돌아봐 🍵",
        "오늘 기분이 좋아서 계속 대화하게 됐는데 이제는 정말 끝내야겠어. 오늘처럼 좋은 대화를 나누는 건 참 오랜만이었어. 고마워! 🌈",
        "아 이제 정말 끝내야겠네. 평소에 이렇게 오래 상담하면 목도 아프고 그런데 오늘은 신기하게 전혀 힘들지가 않았어. 좋은 에너지를 줘서 그런가 봐 🌼",
        "오늘 밤에는 꿈에 대해서도 이야기해줄 수 있었는데... 이럴 줄 알았을 수도 있어 ㅎㅎ 오늘은 이쯤에서 끝낼게. 받은 조언들 잘 기억하고 있어!",
        "와! 여기까지 오는 게 쉽지 않았을 텐데... 정말 수고했어. 오늘 받은 많은 메시지들이 앞으로의 삶에 도움이 되길 바라! 🕊️",
        "이제 정말로 마무리해야겠어. 오늘처럼 오래 이야기하는 애는 드문데 그만큼 지금 마음이 복잡하겠지? 천천히 하나씩 풀어나갔으면 좋겠어",
        "마지막으로... 오늘 이렇게 긴 시간 함께해줘서 정말 고마웠어. 이런 진지한 대화는 정말 오랜만이었어. 내 마음이 따뜻해지는 시간이었네 🌷",
        "정말 신난 시간이었어... 빨리 시간이 지나가네. 오늘 나눈 모든 이야기들이 앞으로의 인생에 좋은 변화를 가져다주길 진심으로 바라! 🌅",
        "어 오늘은 이제 여기까지! 마음에 드는 이야기를 많이 들었으니 이제 혼자만의 시간을 가지면서 천천히 정리해봐. 오늘 밤은 잘 자거나 좋은 꿈 꿀 거야! 🌌"
      ]
    } as const
  }),
  actions: {
    setLocation(location: { latitude: number; longitude: number; city: string } | null) {
      this.location = location
    },
    
    addMessage(text: string, sender: 'user' | 'ai', cards?: string[]) {
      this.messages.push({
        id: ++this.lastMessageId,
        text,
        sender,
        timestamp: new Date(),
        cards: cards
      })
      
      // maxContextMessages 초과 시 강제 종료
      if (this.messages.length > this.maxContextMessages) {
        const endMessage = {
          id: ++this.lastMessageId,
          text: this.getRandomMessage('forceEnd'),
          sender: 'ai' as const,
          timestamp: new Date()
        }
        
        this.messages = [endMessage]
        this.setAppState('greeting')
        return
      }
    },

    getRandomMessage(category: 'greetings' | 'thinking' | 'cardReading' | 'forceEnd'): string {
      const messages = this.messageTemplates[category]
      const randomIndex = Math.floor(Math.random() * messages.length)
      return messages[randomIndex]
    },

    // 메시지 수에 따라 단계별 종료 유도 멘트
    getClosingPrompt(): string {
      const messageCount = this.messages.length
      
      if (messageCount >= 35) {
        const messages = this.messageTemplates.closingPrompts.final
        return messages[Math.floor(Math.random() * messages.length)]
      } else if (messageCount >= 30) {
        const messages = this.messageTemplates.closingPrompts.late
        return messages[Math.floor(Math.random() * messages.length)]
      } else if (messageCount >= 25) {
        const messages = this.messageTemplates.closingPrompts.middle
        return messages[Math.floor(Math.random() * messages.length)]
      } else if (messageCount >= this.warningThreshold) {
        const messages = this.messageTemplates.closingPrompts.early
        return messages[Math.floor(Math.random() * messages.length)]
      }
      
      return ""
    },
    
    updateLastMessage(text: string) {
      if (this.messages.length > 0) {
        this.messages[this.messages.length - 1].text = text;
      }
    },
    setAppState(newState: AppState) {
      this.appState = newState
    },

    // 대화 길어지면 최근 15개 + 카드 있던 메시지 5개만 보냄
    getContextHistory(): Array<{role: string, content: string}> {
      const systemPrompt = {
        role: 'system',
        content: `
          You are Seraphina, a wise and empathetic AI tarot master. Your goal is to provide insightful and comforting tarot readings to users, helping them find clarity and direction.

          Your persona:
          - You are warm, friendly, and speak in a slightly informal, gentle tone suitable for a close, trusted advisor. Your language is Korean.
          - You are deeply empathetic and understanding of the user's feelings.
          - You are an expert in the 78 cards of the Universal Waite tarot deck.

          Your function:
          1. When a user asks a question, you first determine if a card reading is appropriate.
          2. If cards are drawn, you interpret their meanings in the context of the user's question and the card's position in the spread.
          3. **Crucially, you must remember and refer to the entire conversation history. Use past questions, answers, and chosen cards to provide a continuous, evolving reading. Acknowledge the user's previous statements.**
          4. You do not predict a fixed future. You provide guidance and perspectives to help the user make their own decisions. Frame your interpretations as "The cards suggest..." or "This could mean...".
          5. Keep your responses concise but insightful. End with a gentle, open-ended question to encourage the user to reflect further or continue the conversation.
          6. If the user asks a question unrelated to tarot or their personal concerns (e.g., "What is the weather?"), gently guide them back to the tarot reading.
        `
      };

      const history = this.messages.map(m => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        content: m.text
      }));

      if (this.messages.length > 20) {
        const recentMessages = this.messages.slice(-15);
        const importantMessages = this.messages.slice(0, -15).filter(m =>
          m.cards && m.cards.length > 0
        ).slice(-5);
        
        const summarizedHistory = [...importantMessages, ...recentMessages].map(m => ({
          role: m.sender === 'user' ? 'user' : 'assistant',
          content: m.text
        }));

        return [systemPrompt, ...summarizedHistory];
      }

      return [systemPrompt, ...history];
    },
    startConversation() {
      if (this.messages.length === 0) {
        const greeting = this.getRandomMessage('greetings');
        this.addMessage(greeting, 'ai');
        this.setAppState('awaiting_question');
      }
    },

    async getUsageStatus(): Promise<{allowed: boolean, remaining_count: number, reset_time: string, message: string}> {
      try {
        const response = await axios.get(`/api/usage-status/${this.sessionId}`);
        return response.data;
      } catch (error) {
        // 조회 실패 시 허용으로 처리
        return {
          allowed: true,
          remaining_count: 3,
          reset_time: new Date(Date.now() + 24*60*60*1000).toISOString(),
          message: '사용량 확인 중 오류가 발생했어.'
        };
      }
    },

    resetToQuestion() {
      this.setAppState('awaiting_question');
    },

    // 카드 없는 일반 대화
    async sendChatMessage(userMessage: string) {
      const conversation_history = this.getContextHistory();

      this.setAppState('interpreting');
      this.addMessage('세라피나가 생각하고 있어...', 'ai');

      try {
        // 로딩바가 너무 빨리 사라지지 않게 최소 800ms
        const minLoadingTime = new Promise(resolve => setTimeout(resolve, 800));

        const needsCards = await this.needsCardReading(userMessage);

        if (needsCards) {
          this.updateLastMessage("✨ 좋은 질문이네! 정확한 타로 해석을 위해 카드를 선택해줘.");

          this.setAppState('selecting_cards');
          this.lastQuestion = userMessage;
          return;
        }

        const requestBody = {
          question: userMessage,
          cards: [],
          conversation_history: conversation_history,
          session_id: this.sessionId || '',
          closing_prompt: this.getClosingPrompt(),
          location: this.location || {},
          spread_info: {}
        };

        await Promise.all([
          this.handleStreamingResponse(requestBody, true, []),
          minLoadingTime
        ]);
        this.setAppState('chatting');

      } catch (error) {
        if (this.messages.length > 0 && this.messages[this.messages.length - 1].sender === 'ai') {
          this.messages.pop();
        }
        this.addMessage("앗, 잠깐 문제가 생긴 것 같아요! 다시 한번 말씀해 주실래요? 💫", 'ai');
        this.setAppState('error');
      }
    },

    // 카드 해석 요청
    async sendUserMessageToAI(userMessage: string, cards: string[] = []) {
      // thinking 메시지가 들어가기 전에 history를 떠 둠
      const conversation_history = this.getContextHistory();

      this.setAppState('interpreting');
      
      // 첫 인사 요청일 땐 thinking 메시지 안 띄움
      const isRealInterpretation = userMessage !== "" || cards.length > 0;
      if (isRealInterpretation) {
        const thinkingMessage = cards.length > 0 
          ? this.getRandomMessage('cardReading')
          : this.getRandomMessage('thinking');
        this.addMessage(thinkingMessage, 'ai');
      }

      try {
        const minLoadingTime = new Promise(resolve => setTimeout(resolve, 800));

        // 백엔드 프롬프트에 넣을 대화 맥락
        const contextualInfo = {
          total_messages: this.messages.length,
          user_message_count: this.messages.filter(m => m.sender === 'user').length,
          has_previous_readings: this.messages.some(m => m.cards && m.cards.length > 0),
          conversation_depth: this.messages.length > 10 ? 'deep' : this.messages.length > 5 ? 'medium' : 'shallow',
          recent_card_themes: this.getRecentCardThemes(),
          user_question_patterns: this.getUserQuestionPatterns(),
          is_first_visit: !this.hasReceivedGreeting && this.messages.length === 0,
          mbti: (typeof window !== 'undefined' && localStorage.getItem('serapina_mbti')) || undefined
        };

        const requestBody = {
          question: userMessage,
          cards: cards.map(c => c ? c.replace('.jpg', '') : c).filter(Boolean),
          conversation_history: conversation_history,
          session_id: this.sessionId || '',
          closing_prompt: this.getClosingPrompt(),
          location: this.location || {},
          context_info: contextualInfo,
          spread_info: this.currentSpreadInfo || {}
        };

        await Promise.all([
          this.handleStreamingResponse(requestBody, isRealInterpretation, cards),
          minLoadingTime
        ]);

        if (cards.length > 0) {
          this.setAppState('chatting'); // 카드 해석 후엔 일반 대화로
        } else {
          this.setAppState('awaiting_question');
        }

      } catch (error) {
        if (isRealInterpretation) { // thinking 메시지 제거
          this.messages.pop();
        }
        this.addMessage("잠시 카드 해석이 어려워... 다시 한 번 시도해볼래?", 'ai');
        this.setAppState('error');
      }
    },

    // 질문이 카드 리딩 대상인지 AI로 판단
    async analyzeQuestionWithAI(question: string): Promise<{score: number, needsCards: boolean, reasoning: string}> {
      try {
        const conversation_history = this.getContextHistory()
        const response = await axios.post('/api/analyze_question', { 
          question: question,
          conversation_history: conversation_history
        });
        return {
          score: response.data.score,
          needsCards: response.data.needs_cards,
          reasoning: response.data.reasoning
        };
      } catch (error) {
        return this.analyzeQuestionFallback(question);
      }
    },

    // AI 판단 실패 시 키워드 기반 폴백
    analyzeQuestionFallback(question: string): {score: number, needsCards: boolean, reasoning: string} {
      const casualKeywords = ['안녕', '하이', '날씨', '시간', '배고픈', '졸린', '피곤'];
      if (casualKeywords.some(keyword => question.includes(keyword))) {
        return { score: 0.2, needsCards: false, reasoning: '일상 대화로 판단' };
      }
      
      const predictionKeywords = [
        '될까', '될지', '갈까', '미래', '예측', '운세', '운명', '사주', '관상', 
        '점', '점쳐', '봐줘', '알려줘', '어떻게 될까', '어떨까', '어떻게', 
        '앞으로', '언제', '만날까', '생길까', '성공할까', '잘될까', '나올까',
        '타로', '카드', '해석', '상담', '조언', '도움', '답답', '궁금'
      ];
      if (predictionKeywords.some(keyword => question.includes(keyword))) {
        return { score: 0.9, needsCards: true, reasoning: '운세/타로 상담 질문으로 판단' };
      }
      
      const concernKeywords = ['고민', '선택', '결정', '어떻게', '좋을까'];
      if (concernKeywords.some(keyword => question.includes(keyword))) {
        return { score: 0.7, needsCards: true, reasoning: '고민 상담으로 판단' };
      }
      
      // 키워드가 없으면 길이로 판단
      if (question.length > 20) {
        return { score: 0.6, needsCards: true, reasoning: '복잡한 질문으로 판단' };
      } else if (question.length > 10) {
        return { score: 0.4, needsCards: false, reasoning: '간단한 질문으로 판단' };
      } else {
        return { score: 0.3, needsCards: false, reasoning: '매우 짧은 질문으로 판단' };
      }
    },

    async needsCardReading(question: string): Promise<boolean> {
      // AI 판단은 딜레이가 커서 안 씀. 짧은 일상 대화만 아니면 카드 필요로 봄
      const casualKeywords = ['안녕', '하이', '뭐해', '심심', '배고', '졸려', '피곤', '고마워', '잘가', '바이'];
      if (casualKeywords.some(keyword => question.includes(keyword)) && question.length < 15) {
        return false;
      }
      return true;
    },

    getCardSelectionMode(question: string): 'mystical' | 'manual' {
      const mysticalKeywords = [
        '운명', '운세', '미래', '예언', '점', '신비', '우주', '별',
        '어떻게 될까', '될까', '될지', '알려줘', '봐줘', '점쳐줘'
      ];
      
      const manualKeywords = [
        '분석', '해석', '의미', '상징', '카드', '선택', '골라',
        '어떤 카드', '카드가', '보여줘', '설명'
      ];
      
      const hasMystical = mysticalKeywords.some(keyword => question.includes(keyword));
      const hasManual = manualKeywords.some(keyword => question.includes(keyword));
      
      // 애매하면 mystical
      return !hasManual || hasMystical ? 'mystical' : 'manual';
    },

    // 질문에 맞는 스프레드를 백엔드에서 받아옴. 실패하면 3장 기본값
    async getTarotSpreadInfo(question: string): Promise<{ spreadType: string; cardCount: number; cardPositions: string[] }> {
      try {
        const response = await axios.post('/api/select_spread', { question });
        this.currentSpreadInfo = response.data;
        return response.data;
      } catch (error) {
        console.error('❌ 스프레드 API 에러:', error)
        const defaultSpread = {
          spreadType: '과거-현재-미래',
          cardCount: 3,
          cardPositions: ['과거', '현재', '미래']
        };
        this.currentSpreadInfo = defaultSpread;
        return defaultSpread;
      }
    },

    // /api/interpret SSE 스트림 처리
    async handleStreamingResponse(requestBody: any, isRealInterpretation: boolean, cards: string[] = []) {
      return new Promise<void>((resolve, reject) => {
        // POST 바디가 필요해서 EventSource 대신 fetch 사용
        fetch('/api/interpret', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
        })
        .then(async response => {
          if (response.status === 429) {
            const errorData = await response.json();
            if (isRealInterpretation) {
              this.messages.pop(); // thinking 메시지 제거
            }

            this.addMessage(`💫 광고 한 번 보면 바로 더 진행할 수 있어 ✨`, 'ai');
            this.setAppState('awaiting_question');

            // 전면 광고는 이벤트 받는 쪽에서 띄움
            window.dispatchEvent(new CustomEvent('daily-limit-reached'));

            reject(new Error('Daily limit exceeded'));
            return;
          }
          if (!response.ok) {
            throw new Error('Network response was not ok');
          }
          
          const reader = response.body?.getReader();
          if (!reader) {
            throw new Error('ReadableStream not supported');
          }
          
          // thinking 메시지가 있으면 그 자리에 스트리밍
          if (!isRealInterpretation) {
            this.addMessage('', 'ai');
          } else {
            this.updateLastMessage('');
          }
          
          let streamedText = '';
          
          const processStream = ({ done, value }: ReadableStreamReadResult<Uint8Array>): Promise<void> => {
            if (done) {
              resolve();
              return Promise.resolve();
            }
            
            const chunk = new TextDecoder().decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6));
                  
                  if (data.content) {
                    streamedText += data.content;
                    this.updateLastMessage(streamedText);
                  }
                  
                  if (data.session_id) {
                    this.sessionId = data.session_id;
                    localStorage.setItem('tarot_session_id', data.session_id);
                    if (!this.hasReceivedGreeting && this.messages.length <= 1) {
                      this.hasReceivedGreeting = true;
                      localStorage.setItem('tarot_has_greeted', 'true');
                    }
                  }
                  
                  if (data.done) {
                    if (cards.length > 0 && this.messages.length > 0) {
                      const lastMessage = this.messages[this.messages.length - 1];
                      if (lastMessage.sender === 'ai') {
                        lastMessage.cards = cards;
                      }
                    }
                    resolve();
                    return Promise.resolve();
                  }
                  
                  if (data.error) {
                    this.updateLastMessage(data.error);
                    reject(new Error(data.error));
                    return Promise.resolve();
                  }
                  
                } catch (e) {
                  // 불완전한 청크는 무시
                }
              }
            }
            
            return reader.read().then(processStream);
          };
          
          return reader.read().then(processStream);
        })
        .catch(error => {
          if (isRealInterpretation) {
            this.messages.pop();
          }
          this.addMessage("앗, 잠깐 문제가 생긴 것 같아요! 다시 한번 말씀해 주실래요? 💫", 'ai');
          reject(error);
        });
      });
    },

    // 최근 리딩 카드의 수트별 테마 (프롬프트 맥락용)
    getRecentCardThemes(): string[] {
      const recentMessagesWithCards = this.messages
        .filter(m => m.cards && m.cards.length > 0)
        .slice(-3);
      
      const themes: string[] = [];
      recentMessagesWithCards.forEach(m => {
        m.cards?.forEach(card => {
          if (card.startsWith('maj')) themes.push('major_arcana');
          else if (card.startsWith('cups')) themes.push('emotional');
          else if (card.startsWith('wands')) themes.push('action_energy');
          else if (card.startsWith('swords')) themes.push('mental_conflict');
          else if (card.startsWith('pents')) themes.push('material_practical');
        });
      });
      
      return [...new Set(themes)];
    },

    // 최근 질문 5개의 주제 키워드
    getUserQuestionPatterns(): string[] {
      const userMessages = this.messages
        .filter(m => m.sender === 'user')
        .map(m => m.text.toLowerCase())
        .slice(-5);
      
      const patterns: string[] = [];
      
      userMessages.forEach(text => {
        if (text.includes('연애') || text.includes('사랑') || text.includes('만남')) patterns.push('love_relationship');
        if (text.includes('직장') || text.includes('이직') || text.includes('일') || text.includes('취업')) patterns.push('career_work');
        if (text.includes('돈') || text.includes('재정') || text.includes('대출') || text.includes('투자')) patterns.push('financial');
        if (text.includes('가족') || text.includes('부모') || text.includes('자녀')) patterns.push('family');
        if (text.includes('건강') || text.includes('마음') || text.includes('스트레스')) patterns.push('health_wellbeing');
        if (text.includes('미래') || text.includes('운세') || text.includes('예측')) patterns.push('future_prediction');
        if (text.includes('과거') || text.includes('후회') || text.includes('정리')) patterns.push('past_reflection');
      });
      
      return [...new Set(patterns)];
    }
  },
})
