# Project Sovereign — Workflow & Implementation Roadmap

This document contains the complete end-to-end workflow, architectural decisions, and phased implementation plan for **Project Sovereign**.

---

## 🏛️ System Architecture Overview

```text
Next.js (Port 3008)
├── Server Components      ← SSR / Server prefetching (sessions, message history)
├── Client Components      ← Interactive chat UI (messages, inputs, keyboard shortcuts)
├── Server Actions         ← Server-side mutations (create/delete session, cache revalidation)
└── SSE Client             ← Real-time token streaming parser (POST /api/v1/chat/stream)
          ↓
   FastAPI Backend (Port 3009)
          ↓
   Sovereign Brain (Orchestrator, Planner, Memory & Knowledge RAG)
          ↓
   LLMProvider Interface ➔ OllamaAdapter
          ↓
   Ollama (Port 11434: Local Models: Qwen2.5 / Qwen3, EmbeddingGemma)
          ↓
   PostgreSQL + pgvector (Port 5434: Sessions, Messages, Memories, Knowledge)
```

---

## 🔮 Future Architecture Evolution: Next.js as BFF + Prisma

As the application scales, Next.js can evolve into a **Backend-For-Frontend (BFF)** layer equipped with **Prisma** for direct application state and database access:

```text
                 ┌──────────────────────┐
                 │       Browser        │
                 │  React / Next.js UI  │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │      Next.js         │
                 │   Frontend + BFF     │
                 │                      │
                 │ Server Components    │
                 │ Server Actions       │
                 │ API Routes           │
                 │ Prisma               │
                 └───────┬───────┬──────┘
                         │       │
                    PostgreSQL   │ HTTP / SSE
                                │
                                ▼
                    ┌──────────────────┐
                    │     FastAPI      │
                    │ Sovereign Brain  │
                    └────────┬─────────┘
                             │
                             ▼
                          Ollama
```

### Role Separation:
1. **Next.js (Frontend + BFF)**:
   - Manages user accounts, application preferences, UI caches, and session metadata via **Prisma**.
   - Serves Server Components, Server Actions, and proxies AI requests to FastAPI.
2. **FastAPI (Sovereign Brain)**:
   - Remains the dedicated, unencumbered **cognitive intelligence engine**.
   - Responsible for agent loops, tool sandboxing, knowledge vector search (`pgvector`), and Ollama model dispatch.


---

## 🔄 Core Cognitive Workflow (The Native Agent Loop)

```text
┌─────────────────────────────┐
│            USER             │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│      SOVEREIGN BRAIN        │
│                             │
│ 1. Understand request       │
│ 2. Build task context       │
│ 3. Decide next action       │
└──────────────┬──────────────┘
               │
               ▼
        ┌──────────────┐
        │   Decision   │
        └──────┬───────┘
               │
       ┌───────┼────────┐
       │       │        │
       ▼       ▼        ▼
    Answer  Retrieve   Tool
             Context    Call
                         │
                         ▼
                      Permission Check (Python-enforced)
                         │
                         ▼
                      Execute Tool
                         │
                         ▼
                       Observe Result
                         │
                         ▼
                     Brain Evaluates
                         │
                  ┌──────┴──────┐
                  ▼             ▼
               Continue       Finish
```

### Golden Rule: Simple Requests Stay Simple
- **Simple Question** (`"What is Python?"`):
  `Brain ➔ Ollama ➔ Direct Answer`
  *(No planner overhead, no web search, no filesystem access, no unnecessary memory lookup).*
- **Complex Task** (`"Audit project files and recommend hosting"`):
  `Brain ➔ Planner ➔ Tool Registry (Files / Web) ➔ Observe ➔ Reason ➔ Final Answer`.

---

## 🗺️ Phased Implementation Roadmap

| Phase | Description | Status | Details |
| :--- | :--- | :---: | :--- |
| **Phase 1** | **FastAPI + Brain + Ollama Abstraction** | ✅ Done | `BrainOrchestrator` decoupled via `LLMProvider` and `OllamaAdapter`. On-demand model lifecycle with `keep-alive`. |
| **Phase 2** | **Sessions & Messages Persistence** | ✅ Done | PostgreSQL async database via SQLAlchemy 2.0. Alembic migrations for `sessions` and `messages`. |
| **Phase 3** | **Next.js Frontend & SSE Integration** | ✅ Done | Port 3008. Server Components (SSR), Client Components, Server Actions, and resilient SSE streaming client. |
| **Phase 4** | **Long-Term Memory** | 🔄 Next | Curated extraction of user facts, preferences, goals, and recurring context into PostgreSQL. Not blindly storing every message. |
| **Phase 5** | **Tool Registry & Permission Guardrails** | 🔄 Ready | Centralized registry (`modules/tools/`). Read-only safe tools vs. confirmation-gated mutations (`delete`, `modify`, `deploy`, `git push`). |
| **Phase 6** | **Knowledge Ingestion & pgvector RAG** | 🔄 Ready | Document extraction, chunking, Ollama embeddings (`nomic-embed-text` / `embeddinggemma`), and semantic similarity search. |
| **Phase 7** | **Planner & Multi-Step Execution** | 🔄 Ready | Dynamic plan generation and execution loop for complex multi-step tasks. |
| **Phase 8** | **Advanced Security & Confirmations** | 🔄 Ready | User confirmation flow for destructive tool actions via API/UI. |
| **Phase 9** | **Production Hardening & Deployment** | 🔄 Ready | Docker production profiles, reverse proxy (Caddy/Nginx), and security audit. |

---

## ⚙️ Ports & Configuration Reference

- **Frontend**: [http://localhost:3008](http://localhost:3008)
- **FastAPI API**: [http://localhost:3009](http://localhost:3009)
- **FastAPI Swagger Docs**: [http://localhost:3009/docs](http://localhost:3009/docs)
- **PostgreSQL Database**: Port `5434` (mapped from container `5432`)
- **Ollama AI Runtime**: [http://localhost:11434](http://localhost:11434)
