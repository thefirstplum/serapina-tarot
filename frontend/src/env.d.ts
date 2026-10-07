/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_URL: string
  readonly VITE_APP_NAME: string
  readonly VITE_GA_ID: string
  readonly VITE_API_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

// Google Analytics
interface Window {
  dataLayer?: any[]
  gtag?: (...args: any[]) => void
}
