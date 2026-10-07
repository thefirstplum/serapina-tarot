# Serapina

AI tarot reading service powered by a self-hosted LLM | https://serapina.kr

English | [한국어](README.md)

## Overview

A project to test whether a conversational AI service can run on a local LLM alone, with no external API cost. Tarot was chosen as the domain because each card has an established system of meanings: the core interpretation knowledge is supplied through prompts and RAG, and the LLM produces a reading that fits the context of the question. Built and operated by one person.

This repository is a public copy of the private original, with secrets and production data removed.

## Features

- Spread selection based on question intent (time expressions only adjust timing)
- RAG over card interpretation knowledge (ChromaDB, ko-sroberta-multitask)
- SSE streaming, a single GPU queue with queue position shown to the user
- Crisis-signal detection (explicit phrases handled immediately, ambiguous ones re-checked by a classification prompt)
- PII masking before text reaches the LLM, encrypted storage of questions and readings
- Startup self-check of card data, spreads, RAG and encryption
- 5 languages

## Architecture

```
Browser --HTTPS--> Nginx (static files, prerendered HTML, /api proxy)
                     |
                   FastAPI (single uvicorn worker)
                   intent -> spread -> expert prompt
                   -> RAG search -> LLM queue -> SSE
                     |                          |
                   MySQL (encrypted Q&A)      Ollama (host, GPU)
```

- LLM: Ollama `qwen3.6:35b-a3b`, replacing the initial gemma3 because of coherence and wording issues in long answers
- Ollama runs on the host, outside Docker, to use the GPU (Metal)
- A Claude API path also exists: Ollama by default, switched with `AI_PROVIDER=CLAUDE` plus `CLAUDE_API_KEY`, falling back to Ollama when the key is missing
- Details in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) (Korean)

## Key engineering work

- Concurrent requests on a single GPU: one worker, serialized LLM calls, queue position over SSE
- Fixed the RAG similarity calculation and added a startup self-check
- Spread selection that separates question intent from time expressions
- Fixed post-deploy page freezes caused by service worker caching
- Quality checks against 499 real questions from tarot communities

Details in [docs/NOTES.md](docs/NOTES.md) (Korean).

## Stack

- Frontend: Vue 3, TypeScript, Vuetify 3, Pinia, Vite
- Backend: FastAPI, SQLAlchemy 2.0 (async), MySQL 8.0
- AI and retrieval: Ollama, ChromaDB, sentence-transformers
- Infrastructure: Docker Compose, Nginx, Let's Encrypt

## Running locally

Requires Node.js 20.19+ or 22.12+, Python 3.11+, Docker Compose, and [Ollama](https://ollama.ai) installed on the host.

```bash
cp .env.example .env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# set the secrets (ENCRYPTION_PASSWORD, SECRET_KEY, ...) in both .env files to random values

ollama pull qwen3.6:35b-a3b
docker compose up -d mysql

cd backend && pip install -r requirements.txt
uvicorn main:app --reload        # http://localhost:8000/docs

cd ../frontend && npm install
npm run dev                      # http://localhost:5173
```

The RAG index (about 145 MB) is not in the repo. Without it the service runs without RAG; build it with the pipeline in `backend/scripts/` (subtitle collection, cleanup, LLM rewrite, indexing). Deploy and rollback scripts are described in [scripts/README.md](scripts/README.md) (Korean).

## Docs (Korean)

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) structure and data flow
- [docs/NOTES.md](docs/NOTES.md) engineering issues, fixes and next steps
- [docs/AI-COLLABORATION.md](docs/AI-COLLABORATION.md) notes on working with AI tools

## License

Code is [MIT licensed](LICENSE). Card artwork is from the Rider-Waite deck (1909, Pamela Colman Smith), which is in the public domain. See [ATTRIBUTION.md](ATTRIBUTION.md).
