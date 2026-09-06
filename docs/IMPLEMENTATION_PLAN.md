# Project Sovereign — Python Sovereign Brain & Next.js Application Shell

> **Persistent Blueprint for Sovereign Cognitive Platform**
>
> **Core Principle:** Next.js handles the application. Python/FastAPI is the Sovereign Brain — orchestration, memory, knowledge, tools, and planning.
>
> **Architecture Direction:** Next.js Application Monolith + FastAPI Sovereign Brain + PostgreSQL/pgvector + Ollama
>
> See [ARCHITECTURE_DECISION.md](ARCHITECTURE_DECISION.md) for why this direction was chosen over an earlier draft that proposed moving cognition into Next.js.

---

# 🏛️ System Architecture

```text
PROJECT SOVEREIGN

Next.js (Port 3008)
├── UI (login optional — chat/sessions work with no account)
├── NextAuth (Credentials + JWT) + BFF under src/app/api/**
├── SSE proxy to FastAPI (/api/chat/stream)
└── Rate limiting (login only)
        │           │
        │           └──► Redis (Port 6380) — login rate-limit counters only
        ▼
   Postgres (Port 5435) — Next.js's OWN database, via Prisma
   ├── User (email/passwordHash, sessionVersion for "sign out everywhere")
   └── LoginSession (login history — IP, user-agent, timestamp)
        │
        ▼ server-only fetch, FASTAPI_INTERNAL_URL
Python / FastAPI — Sovereign Brain (Port 3009)
├── Brain orchestration & decisions
├── Context Engine
├── Long-term memory (extraction + hybrid retrieval)
├── Knowledge / RAG (ingestion, chunking, pgvector search)
├── Tool Registry & Permission Guardrails
├── Planner (multi-step execution)
├── LLM abstraction / Ollama adapter
├── Streaming
└── Embeddings
        │
        ▼
Ollama (Port 11434)
├── Qwen 2.5
├── Qwen Coder
└── Other local models

        ▼
PostgreSQL + pgvector (Port 5434) — FastAPI's OWN database, separate from Next.js's
├── Sessions & Messages (sessions.user_id optionally tags the Next.js user, if any)
├── Summaries
├── Memories
├── Knowledge Chunks
└── Tool Executions & Audit Logs (executed_by optionally attributes the Next.js user)
```

Two separate Postgres databases, two separate ORMs (Prisma / SQLAlchemy) — this is deliberate, not an oversight. Next.js's database holds only login-related data; everything else stays in FastAPI's database. Neither ORM ever writes to the other's tables.

### The Unbreakable Principle:

> **Next.js = application shell (UI, auth, BFF)**  
> **Python/FastAPI = Sovereign brain/behavior + model layer**  
> **Ollama = local inference**  
> **No third backend language/runtime.**

---

# 🎯 Core Architectural Decision

Project Sovereign will **not replace the existing Python/Ollama model layer unnecessarily**.

Python/FastAPI remains responsible for communicating with Ollama and handling the low-level model/inference responsibilities.

Sovereign focuses on providing the **cognitive behavior, orchestration, memory, tools, context, planning, and decision-making** around the model.

The goal is not to rebuild Ollama functionality in Next.js.

The goal is to make the model behave as part of a larger Sovereign cognitive system.

```text
┌──────────────────────────────────────┐
│           SOVEREIGN                  │
│                                      │
│ Context                              │
│ Memory                               │
│ RAG                                  │
│ Tools                                │
│ Permissions                          │
│ Confirmations                        │
│ Planner                              │
│ Agent Behavior                       │
│ Model Routing                        │
│ Conversation Logic                   │
│ Audit                                │
└──────────────────┬───────────────────┘
                   │
                   │ Model Request
                   ▼
┌──────────────────────────────────────┐
│        PYTHON MODEL SERVICE          │
│                                      │
│ LLM Provider                         │
│ Ollama Adapter                       │
│ Streaming                            │
│ Generation                           │
│ Embeddings                           │
│ Model Communication                  │
└──────────────────┬───────────────────┘
                   │
                   ▼
┌──────────────────────────────────────┐
│              OLLAMA                  │
│                                      │
│ Qwen                                 │
│ Qwen Coder                           │
│ Other Local Models                   │
└──────────────────────────────────────┘
```

---

# 🧱 Clear Responsibility Boundaries

### 1. Python / FastAPI Model Service (Port 3009)
* Dedicated interface for model communication and inference.
* Abstract `LLMProvider` interface and concrete `OllamaAdapter`.
* Native token streaming via async generators.
* Local embeddings generation (`embeddinggemma`, `nomic-embed-text`).
* Generation parameters (temperature, context window, keep-alive).
* Model dispatch and switching (`qwen2.5`, `qwen2.5-coder`).

### 2. Sovereign Cognitive Behavior
* **Context Engine**: Token budgeting, rolling summarization, and sliding-window context assembly.
* **Long-Term Memory**: Intent-driven memory extraction and hybrid retrieval (SQL + pgvector cosine similarity).
* **Knowledge / RAG**: Document parsing, chunking, and contextual citations.
* **Tool Registry & Permission Guardrails**: Centralized capabilities, safety classification (`READ_ONLY`, `LOW_RISK`, `CONFIRMATION_REQUIRED`), and path sandboxing.
* **Planner**: Progressive autonomy (simple requests stay direct; multi-step complex tasks invoke step-by-step reasoning).

### 3. Next.js Application Monolith + BFF (Port 3008)
* React 19 UI, App Router, and Tailwind design system.
* Server Components and Server Actions.
* Streaming chat consumer with resilient SSE parser.
* Interactive User Confirmation UI for hazardous tool execution approvals.
* Application state, user preferences, and Prisma ORM data access.

---

# 📊 Implementation Roadmap & Status Tracker

| Phase | Subsystem | Key Deliverables | Status |
| :---: | :--- | :--- | :---: |
| **Phase 1** | **FastAPI + Brain + Ollama Abstraction** | Abstract `LLMProvider`, `OllamaAdapter`, Docker Compose (:3009, :5434) | ✅ **Completed** |
| **Phase 2** | **Sessions + Messages Persistence** | SQLAlchemy 2.0 Async, Alembic migrations, CRUD API routes | ✅ **Completed** |
| **Phase 3a** | **Next.js Chat UI + SSE Consumption** | Chat UI, markdown rendering, sidebar, browser-side SSE stream parsing | ✅ **Completed** |
| **Phase 3b** | **Next.js Application Monolith / BFF** | Internal API routes (`src/app/api/`) proxying FastAPI, SSE proxy, Prisma + user accounts, Auth (NextAuth/Auth.js), login history + "sign out everywhere", Redis login rate-limiting | ✅ **Completed** — login is intentionally **optional**: chat/sessions work with no account; logging in adds session/audit attribution, login history, and revocation. No durable user-preferences feature exists yet (nothing to store there so far). |
| **Phase 4** | **Conversation History & Context Engine** | `conversation_summaries`, sliding window, token budgeting, Context Engine | ✅ **Completed** |
| **Phase 5** | **Long-Term Memory & Hybrid Retrieval** | `memories` table, structured fact extraction + pgvector cosine similarity | ✅ **Completed** |
| **Phase 6** | **Tool Registry & Permission Guardrails** | Centralized tool registry, safety classification (read-only vs dangerous) | ✅ **Completed** |
| **Phase 7** | **Tool Confirmation Workflow & Audit Trail** | Interactive UI confirmation cards, approve/reject endpoints, `tool_executions` audit trail | ✅ **Completed** |
| **Phase 8** | **Knowledge Ingestion & pgvector RAG** | `ingestion.py`/`retrieval.py` scaffolding exists; still missing: `knowledge/service.py` aggregator (currently empty), document upload pipeline (PDF/DOCX/TXT), grounded citations | 🔄 **In Progress** |
| **Phase 9** | **Planner & Autonomous Multi-Step Loop** | Only a keyword-matching dispatcher exists (`brain/decisions.py`); no plan-step-observe-reflect loop yet | 📋 Planned |
| **Phase 10** | **Production Hardening** | Login rate-limiting done (Next.js side, Redis). Still missing: FastAPI-side API auth (`core/security.py`, currently empty), structured request logging (`core/logging.py`, currently empty), model routing (Qwen vs Coder), GPU keep-alive/idle unload, deployment automation | 🔄 In Progress |

> This table is the single source of truth for phase status. `ARCHITECTURE.md` and `WORKFLOW_AND_ROADMAP.md` link here rather than keeping their own copies — the project has drifted out of sync three times from duplicated status tables going stale independently.
>
> Expanding tools/skills (new file operations, real web search, weather, a coding agent, etc.) extends Phases 6–10 above — see `IMPLEMENTATION_SKILL_PLAN.md` for the draft evaluation. It is explicitly not a competing Phase 0–10; don't let it become a fourth tracker.

---

# 🔐 Permission Model

### READ-ONLY (Auto-Approved)
Safe, read-only environmental inspection:
* `read_file` (with line limits)
* `list_directory` (file metadata)
* `git_status` (working tree check)
* `git_log` (commit history)
* `web_search` (documentation lookup)

### LOW-RISK (Auto-Approved)
Safe sandboxed computations:
* `calculator` (math expressions)
* Scratchpad / temporary data generation

### CONFIRMATION REQUIRED (Explicit Human Consent)
Mutating or destructive operations:
* File writes / modifications (`write_file`)
* File deletions
* Git commits & git pushes
* Destructive SQL operations (`DROP`, `TRUNCATE`, bulk `DELETE`)

The model can request an action. The model cannot authorize itself.

---

# 🔒 Non-Negotiable Engineering Rules

1. **Local-First Only**
   * No OpenAI API, no Anthropic, no Gemini, no OpenRouter.
   * Ollama is the exclusive local inference gateway.

2. **Native Cognitive Architecture**
   * No LangChain, no LlamaIndex, no CrewAI, no OpenClaw runtime.
   * Native orchestration engineered for Project Sovereign.

3. **Pragmatic Technology Allocation**
   * Python handles the model.
   * Sovereign handles the behavior.
   * Next.js handles the application and user confirmation UX.

4. **Simple Requests Stay Simple**
   * Never activate planner or tools unless the request warrants it.

5. **Security by Default**
   * Destructive operations strictly require user confirmation.
   * Tool executions are fully logged in the audit trail.

6. **Git Attribution**
   * All commits must be authored strictly by:
     `Reign Mark Valdez <valdezreignmark@gmail.com>`
   * No `Co-authored-by:` lines.
   * No AI signatures.
