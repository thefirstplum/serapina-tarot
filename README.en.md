# Serapina: AI Tarot Reading Service

English | [한국어](README.md)

A web service that gives tarot readings with a locally hosted LLM. It picks a spread that fits the intent of the question, then interprets the cards the user draws together with tarot knowledge retrieved by RAG, streaming the answer over SSE.

Live: https://serapina.kr (Korean)

A personal project I build and run on my own. Size: about 10.7k lines of Python (including 2k lines of card data), 22 REST/SSE endpoints, 18 MySQL tables, about 20.3k lines of Vue SFC (28 views, 13 components) and 4.1k lines of TypeScript, 5 locales.

This repo is a copy of the private original with secrets and production data removed.

## Stack

- Frontend: Vue 3, TypeScript, Vuetify 3, Pinia, Vite
- Backend: FastAPI, SQLAlchemy 2.0 (async), MySQL 8.0
- AI / retrieval: Ollama (local LLM), ChromaDB, sentence-transformers (`jhgan/ko-sroberta-multitask`)
- Infrastructure: Docker Compose, Nginx, Let's Encrypt (certbot)

## Architecture

```
Browser --HTTPS--> Nginx (static files, prerendered HTML, /api proxy)
                     |
                   FastAPI (single uvicorn worker)
                   intent -> spread -> expert prompt
                   -> RAG search -> LLM queue -> SSE
                     |                          |
                   MySQL (encrypted readings)  Ollama (on the host, GPU)
```

Ollama runs on the host because Docker on macOS cannot use the GPU (Metal); inside a container one reading took minutes. Before a question reaches the LLM, personal data such as phone and bank account numbers is masked ([`sanitizer.py`](backend/sanitizer.py)), and questions and readings are stored encrypted with Fernet ([`encryption.py`](backend/encryption.py)). More detail in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) (Korean).

## Problems and fixes

One GPU, concurrent requests. Overlapping requests slowed everything down until they timed out, so a semaphore runs one LLM call at a time and the number of waiting users goes out over SSE ("N people ahead of you"). The queue screen still showed up only now and then. uvicorn was running `--workers 4`, each process had its own semaphore, and up to four requests were hitting the GPU at once. It now runs one worker.

RAG that returned nothing for almost a year. The index returns unnormalized L2 distances (80 to 190), but the code computed similarity as `1 - distance`, which was always 0, so every result fell under the threshold. A `try/except` swallowed the failure and the LLM filled the gap plausibly, so there was no error and no obviously wrong output. Around the same time I found that the descriptions of all 56 minor arcana cards were empty. Similarity is now computed as cosine directly, and a startup self-check ([`selfcheck.py`](backend/selfcheck.py)) exercises the card data, spread definitions, RAG search, and encryption once.

Intent versus time expressions. "Can I change jobs this week?" was routed to a weekly-fortune spread that listed day-by-day fortunes and never answered the question. "This week" is a condition and "can I" is the intent, so intent is decided first to pick the spread, and time expressions only adjust timing ([`question_intent.py`](backend/question_intent.py)). Five-card answers were also cut off partway: the prompt had grown to about 6,900 tokens while `num_ctx` was fixed at 8192. Context size is now chosen from the prompt length.

Crisis signals. The service was planned for teenagers, so it assumes phrases like "I want to die" will come in. Catching every keyword would also flag "I died on that exam", so explicit phrases are handled right away and only ambiguous ones go through a short classification prompt (`temperature=0`, YES/NO). If the classifier call fails, the message is treated as a crisis.

Pages stuck after a deploy. The API returned 200, but returning visitors saw a frozen screen. The service worker served `index.html` cache-first, so after each deploy they requested old JS chunks and got 404s. HTML is now network-first, and a failed chunk load clears the cache and reloads once.

## Working with AI (Claude Code)

I built and ran this with Claude Code. In the private original, 53 of 69 commits are co-authored by Claude, and 51 landed in the first two weeks. After that the project sat mostly untouched for about six months, and the problems above surfaced in September 2026 when I started reading full answers.

The AI has no memory between sessions, so `CLAUDE.md` holds the structure, commands, and runbooks, and every session reads it. From July 2026 the AI also writes a work log at the end of each session, and a comment I leave from my phone is the first thing the next session acts on. Most changes in direction came from those comments. When I said readings felt vague, the AI started adjusting tone; tracing the input showed that card descriptions and RAG results were empty. It was also testing with tidy questions it wrote itself, so I had it switch to 499 real questions from tarot communities, and the spread and truncation problems above came out of running that set.

Commands to reproduce the numbers and a summary of the work log: [docs/AI-COLLABORATION.md](docs/AI-COLLABORATION.md) (Korean).

## Known limitations

- No automated regression tests or CI. The eval set is run by script and the answers are read by a person. `backend/test_*.py` are manual check scripts.
- `main.py` is a single file of about 3,400 lines with the Ollama/Anthropic switching code spread through it. Logging is `print`.
- The PBKDF2 salt is hardcoded. In crisis classification, a non-200 response from Ollama still falls through to "not a crisis".
- The payments, points, and Kakao login modules are implemented but not wired into the live service.
- The September fixes are in this copy but not yet committed in the private original.

## Running locally

Requires Node.js 20.19+ or 22.12+, Python 3.11+, Docker Compose, and [Ollama](https://ollama.ai) installed on the host.

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# set ENCRYPTION_PASSWORD, SECRET_KEY, JWT_SECRET_KEY to random values

ollama pull gemma3:12b
docker compose up -d mysql

cd backend && pip install -r requirements.txt
uvicorn main:app --reload        # http://localhost:8000/docs

cd ../frontend && npm install
npm run dev                      # http://localhost:5173
```

The RAG index (about 145 MB) is not in the repo. Without it the service runs without RAG; build it with the pipeline in `backend/scripts/` (subtitle collection, cleanup, LLM rewrite, indexing). Deploy and rollback scripts are described in [scripts/README.md](scripts/README.md) (Korean).

## License

Code is [MIT licensed](LICENSE). Card artwork is from the Rider-Waite deck (1909, Pamela Colman Smith), which is in the public domain. See [ATTRIBUTION.md](ATTRIBUTION.md).
