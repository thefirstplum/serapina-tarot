#!/usr/bin/env node
/**
 * SEO/AdSense용 SPA 경로 prerender
 * 사용: node scripts/prerender.js
 *
 * dist를 정적 서버(5050)로 띄우고 puppeteer로 각 경로를 렌더한 뒤
 * dist/{path}/index.html 로 저장. nginx try_files가 이 파일을 먼저 서빙함.
 */
import puppeteer from 'puppeteer'
import http from 'node:http'
import handler from 'serve-handler'
import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const ROOT = path.resolve(__dirname, '..')
const DIST = path.join(ROOT, 'dist')
const PORT = 5050
const BACKEND_HOST = 'localhost:8000' // 로컬 dev 시 백엔드

// Prerender 대상 경로
const STATIC_ROUTES = [
  '/',
  '/about',
  '/contact',
  '/privacy',
  '/terms',
  '/blog',
  '/guides',
  '/guides/love',
  '/guides/career',
  '/guides/study',
  '/guides/money',
  '/cards',
  '/cards/major-arcana',
  '/cards/minor-arcana',
  '/cards/suit/wands',
  '/cards/suit/cups',
  '/cards/suit/swords',
  '/cards/suit/pentacles',
]

async function fetchBlogIds() {
  // 공개된 블로그 ID 가져오기
  return new Promise((resolve) => {
    http.get(`http://${BACKEND_HOST}/blog?limit=100`, (res) => {
      let body = ''
      res.on('data', (c) => (body += c))
      res.on('end', () => {
        try {
          const data = JSON.parse(body)
          resolve((data.posts || []).map((p) => p.id))
        } catch {
          resolve([])
        }
      })
    }).on('error', () => resolve([]))
  })
}

async function fetchCardIds() {
  // 78장 카드 ID 가져오기
  try {
    const cardsModule = await fs.readFile(path.join(ROOT, 'src/data/cardDatabase.ts'), 'utf-8')
    const matches = [...cardsModule.matchAll(/^\s*['"`](\w+)['"`]\s*:\s*\{/gm)]
    return matches.map((m) => m[1])
  } catch (e) {
    console.warn('cardDatabase 읽기 실패:', e.message)
    return []
  }
}

async function startStaticServer() {
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      // /api/* 는 백엔드로 프록시 (blog 본문 fetch용)
      if (req.url.startsWith('/api/')) {
        const proxyReq = http.request({
          host: 'localhost',
          port: 8000,
          path: req.url.replace(/^\/api/, ''),
          method: req.method,
          headers: req.headers,
        }, (proxyRes) => {
          res.writeHead(proxyRes.statusCode, proxyRes.headers)
          proxyRes.pipe(res)
        })
        proxyReq.on('error', (e) => {
          res.writeHead(502)
          res.end(`Proxy error: ${e.message}`)
        })
        req.pipe(proxyReq)
        return
      }
      // SPA fallback: 나머지는 index.html
      return handler(req, res, {
        public: DIST,
        rewrites: [{ source: '**', destination: '/index.html' }],
      })
    })
    server.listen(PORT, () => {
      console.log(`[prerender] 정적 서버 + API 프록시 띄움 http://localhost:${PORT}`)
      resolve(server)
    })
  })
}

async function prerenderRoute(browser, route) {
  const page = await browser.newPage()
  try {
    await page.goto(`http://localhost:${PORT}${route}`, {
      waitUntil: 'networkidle0',
      timeout: 30000,
    })
    // Vue 렌더 대기: body 텍스트 800자 이상 또는 최대 12초
    await page.waitForFunction(
      () => document.body.innerText.length > 800,
      { timeout: 12000 }
    ).catch(() => {})
    // 비동기 fetch 마무리 여유
    await new Promise((r) => setTimeout(r, 2000))

    let html = await page.content()

    // 저장 경로
    const targetDir = route === '/' ? DIST : path.join(DIST, route)
    await fs.mkdir(targetDir, { recursive: true })
    const targetFile = path.join(targetDir, 'index.html')
    await fs.writeFile(targetFile, html, 'utf-8')

    const textLen = (await page.evaluate(() => document.body.innerText.length)) || 0
    console.log(`  ✅ ${route.padEnd(35)} → ${textLen}자 (${html.length} bytes)`)
  } catch (e) {
    console.log(`  ⚠️ ${route.padEnd(35)} 실패: ${e.message.slice(0, 60)}`)
  } finally {
    await page.close()
  }
}

async function main() {
  console.log('[prerender] 시작\n')

  // 1) 동적 경로 수집
  const blogIds = await fetchBlogIds()
  const cardIds = await fetchCardIds()
  console.log(`[prerender] 블로그 ${blogIds.length}개, 카드 ${cardIds.length}장 발견\n`)

  const dynamicRoutes = [
    ...blogIds.map((id) => `/blog/${id}`),
    ...cardIds.slice(0, 30).map((id) => `/cards/${id}`), // 78장 전부는 너무 오래 걸려 일부만
  ]
  const allRoutes = [...STATIC_ROUTES, ...dynamicRoutes]
  console.log(`[prerender] 총 ${allRoutes.length}개 경로 prerender 진행\n`)

  // 2) 정적 서버 시작
  const server = await startStaticServer()

  // 3) puppeteer 띄우기
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox'],
  })

  // 4) 각 경로 prerender (병렬 4개씩)
  const BATCH = 4
  for (let i = 0; i < allRoutes.length; i += BATCH) {
    const batch = allRoutes.slice(i, i + BATCH)
    await Promise.all(batch.map((r) => prerenderRoute(browser, r)))
  }

  await browser.close()
  server.close()
  console.log('\n[prerender] 완료 ✅')
}

main().catch((e) => {
  console.error('[prerender] 에러:', e)
  process.exit(1)
})
