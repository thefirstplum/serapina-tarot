import { defineStore } from 'pinia'
import axios from 'axios'

interface PointProduct {
  code: string
  name: string
  points: number
  price: number
  bonus_points: number
  description: string
  is_popular: boolean
}

interface PointCostItem {
  feature_code: string
  name: string
  cost: number
  description: string
}

interface PointHistoryItem {
  id: number
  usage_type: string
  amount: number
  balance_after: number
  description: string
  created_at: string
}

export const usePointStore = defineStore('point', {
  state: () => ({
    products: [] as PointProduct[],
    costs: [] as PointCostItem[],
    history: [] as PointHistoryItem[],
    showConsumptionDialog: false,
    pendingConsumption: null as {
      featureCode: string
      cost: number
      onConfirm: () => void
      onCancel: () => void
    } | null,
  }),

  getters: {
    getFeatureCost: (state) => (featureCode: string): number => {
      const item = state.costs.find((c) => c.feature_code === featureCode)
      if (item) return item.cost
      const defaults: Record<string, number> = {
        extra_reading: 20,
        premium_reading: 30,
        extra_question: 10,
        special_spread: 50,
      }
      return defaults[featureCode] ?? 20
    },
  },

  actions: {
    async fetchProducts() {
      try {
        const res = await axios.get('/api/points/products')
        this.products = res.data.products
      } catch {
        // 상품 로드 실패
      }
    },

    async fetchCosts() {
      try {
        const res = await axios.get('/api/points/costs')
        this.costs = res.data.costs
      } catch {
        // 비용 로드 실패
      }
    },

    async fetchHistory(limit = 20, offset = 0) {
      try {
        const res = await axios.get('/api/points/history', {
          params: { limit, offset },
        })
        this.history = res.data.history
      } catch {
        // 내역 로드 실패
      }
    },

    requestPointConsumption(
      featureCode: string,
      cost: number,
      onConfirm: () => void,
      onCancel: () => void,
    ) {
      this.pendingConsumption = { featureCode, cost, onConfirm, onCancel }
      this.showConsumptionDialog = true
    },

    confirmConsumption() {
      if (this.pendingConsumption) {
        this.pendingConsumption.onConfirm()
      }
      this.closeConsumptionDialog()
    },

    cancelConsumption() {
      if (this.pendingConsumption) {
        this.pendingConsumption.onCancel()
      }
      this.closeConsumptionDialog()
    },

    closeConsumptionDialog() {
      this.showConsumptionDialog = false
      this.pendingConsumption = null
    },
  },
})
