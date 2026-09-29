import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        dark: false,
        colors: {
          primary: '#7C3AED', // 포인트 보라
          secondary: '#A78BFA', // 부드러운 라벤더
          accent: '#FBBF24', // 밝은 골드
          background: '#FAFAF8', // 따뜻한 오프화이트
          surface: '#FFFFFF',
          'surface-variant': '#F5F3FF', // 연한 보라 표면
          'on-surface': '#1A1A1A', // 다크 텍스트
          'on-primary': '#FFFFFF',
          outline: '#E5E7EB', // 연한 회색 아웃라인
          success: '#10B981', // 민트 그린
          error: '#F43F5E', // 로즈 레드
          info: '#818CF8', // 소프트 인디고
          warning: '#FB923C', // 피치 오렌지
        }
      },
      dark: {
        dark: true,
        colors: {
          primary: '#A78BFA', // 밝은 보라
          secondary: '#C4B5FD', // 밝은 라벤더
          accent: '#FCD34D', // 밝은 골드
          background: '#1A0A2E', // 깊은 보라 배경
          surface: '#2D1B4E', // 약간 밝은 표면
          'surface-variant': '#3F2D5F', // 변형 표면색
          'on-surface': '#EDE9FE', // 연한 보라 텍스트
          'on-primary': '#1A0A2E', // primary 위 텍스트
          outline: '#7C3AED', // 진한 보라 아웃라인
          success: '#34D399', // 밝은 민트
          error: '#FB7185', // 밝은 로즈
          info: '#A5B4FC', // 밝은 인디고
          warning: '#FDBA74', // 밝은 피치
        }
      }
    }
  }
})

export default vuetify
