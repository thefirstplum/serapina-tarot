import { defineStore } from 'pinia'
import axios from 'axios'

interface UserInfo {
  id: number
  nickname: string
  profile_image: string
  email?: string
  point_balance: number
  subscription_tier?: string | null
  subscription_expires_at?: string | null
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as UserInfo | null,
    accessToken: localStorage.getItem('tarot_access_token') || '',
    refreshToken: localStorage.getItem('tarot_refresh_token') || '',
    isLoading: false,
  }),

  getters: {
    isLoggedIn: (state) => !!state.accessToken && !!state.user,
    pointBalance: (state) => state.user?.point_balance ?? 0,
    isPremium: (state) => {
      if (!state.user?.subscription_tier) return false
      if (!state.user?.subscription_expires_at) return false
      return new Date(state.user.subscription_expires_at) > new Date()
    },
  },

  actions: {
    async getKakaoLoginUrl(): Promise<string> {
      try {
        const res = await axios.get('/api/auth/kakao-config')
        const { rest_api_key, redirect_uri } = res.data
        return `https://kauth.kakao.com/oauth/authorize?client_id=${rest_api_key}&redirect_uri=${encodeURIComponent(redirect_uri)}&response_type=code`
      } catch {
        return ''
      }
    },

    async handleKakaoCallback(code: string): Promise<boolean> {
      this.isLoading = true
      try {
        const res = await axios.post('/api/auth/kakao/callback', { code })
        const { access_token, refresh_token, user } = res.data

        this.accessToken = access_token
        this.refreshToken = refresh_token
        this.user = user

        localStorage.setItem('tarot_access_token', access_token)
        localStorage.setItem('tarot_refresh_token', refresh_token)

        this.setupAxiosInterceptor()
        return true
      } catch {
        return false
      } finally {
        this.isLoading = false
      }
    },

    async emailRegister(email: string, password: string, nickname: string): Promise<{ success: boolean; error?: string }> {
      this.isLoading = true
      try {
        const res = await axios.post('/api/auth/register', { email, password, nickname })
        const { access_token, refresh_token, user } = res.data

        this.accessToken = access_token
        this.refreshToken = refresh_token
        this.user = user

        localStorage.setItem('tarot_access_token', access_token)
        localStorage.setItem('tarot_refresh_token', refresh_token)

        this.setupAxiosInterceptor()
        return { success: true }
      } catch (e: any) {
        const msg = e.response?.data?.detail || '회원가입에 실패했어요'
        return { success: false, error: msg }
      } finally {
        this.isLoading = false
      }
    },

    async emailLogin(email: string, password: string): Promise<{ success: boolean; error?: string }> {
      this.isLoading = true
      try {
        const res = await axios.post('/api/auth/login', { email, password })
        const { access_token, refresh_token, user } = res.data

        this.accessToken = access_token
        this.refreshToken = refresh_token
        this.user = user

        localStorage.setItem('tarot_access_token', access_token)
        localStorage.setItem('tarot_refresh_token', refresh_token)

        this.setupAxiosInterceptor()
        return { success: true }
      } catch (e: any) {
        const msg = e.response?.data?.detail || '로그인에 실패했어요'
        return { success: false, error: msg }
      } finally {
        this.isLoading = false
      }
    },

    async fetchMe(): Promise<boolean> {
      if (!this.accessToken) return false
      try {
        this.setupAxiosInterceptor()
        const res = await axios.get('/api/auth/me')
        this.user = res.data
        return true
      } catch {
        this.logout()
        return false
      }
    },

    async linkSession(sessionId: string) {
      if (!this.isLoggedIn || !sessionId) return
      try {
        await axios.post('/api/auth/link-session', { session_id: sessionId })
      } catch {
        // 세션 연결 실패 무시
      }
    },

    setupAxiosInterceptor() {
      axios.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`
    },

    logout() {
      this.user = null
      this.accessToken = ''
      this.refreshToken = ''
      localStorage.removeItem('tarot_access_token')
      localStorage.removeItem('tarot_refresh_token')
      delete axios.defaults.headers.common['Authorization']
    },

    async init() {
      if (this.accessToken) {
        await this.fetchMe()
      }
    },

    updatePointBalance(balance: number) {
      if (this.user) {
        this.user.point_balance = balance
      }
    },
  },
})
