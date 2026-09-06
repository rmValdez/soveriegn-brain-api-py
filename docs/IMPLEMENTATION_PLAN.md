# Project Sovereign — Implementation Plan & Progress Tracker

> **Persistent Blueprint for Sovereign Cognitive Platform**  
> *Last Updated: March 2026*

---

## 🏛️ System Architecture Overview

```text
                              ┌──────────────────────┐
                              │       Browser        │
                              │    React / Next.js   │
                              └──────────┬───────────┘
                                         │
                                         ▼
                         ┌────────────────────────────────┐
                         │         NEXT.JS MONOLITH        │
                         │             + BFF               │
                         │                                │
                         │ • React / UI (Port 3008)       │
                         │ • Server Components (SSR)      │
                         │ • Client Components            │
                         │ • Server Actions               │
                         │ • SSE Stream Consumer          │
                         │ • Zustand UI State             │
                         └───────────────┬────────────────┘
                                         │
                                  HTTP / SSE
                                         │
                                         ▼
                         ┌────────────────────────────────┐
                         │          FASTAPI                 │
                         │       SOVEREIGN BRAIN          │
                         │                                │
                         │ • Brain Orchestration (Port 3009)│
                         │ • Context Engine               │
                         │ • Long-Term Memory             │
                         │ • Knowledge / RAG              │
                         │ • Tool Registry & Permissions  │
                         │ • Multi-Step Planner           │
                         │ • LLM Provider (OllamaAdapter) │
                         └───────────────┬────────────────┘
                                         │
                                         ▼
                              ┌──────────────────┐
                              │      Ollama      │
                              │   Port 11434     │
                              │                  │
                              │ Qwen2.5 / Qwen3 │
                              │ EmbeddingGemma  │
                              └──────────────────┘

                         ┌─────────────────────────┐
                         │ PostgreSQL + pgvector   │
                         │ Port 5434               │
                         │                         │
                         │ Users                   │
                         │ Sessions                │
                         │ Messages                │
                         │ Summaries               │
                         │ Memories                │
                         │ Knowledge Chunks        │
                         │ Tool Executions         │
                         └─────────────────────────┘
```

---

## 📊 Phased Roadmap & Progress Status

| Phase | Subsystem | Key Deliverables | Status |
| :---: | :--- | :--- | :---: |
| **Phase 1** | **FastAPI + Brain + Ollama Abstraction** | Abstract `LLMProvider`, `OllamaAdapter`, Docker Compose (:3009, :5434) | ✅ **Completed** |
| **Phase 2** | **Sessions + Messages Persistence** | SQLAlchemy 2.0 Async, Alembic migrations, CRUD API routes | ✅ **Completed** |
| **Phase 3** | **Next.js + SSE Client UI** | Next.js 15 FAOS App Router (:3008), SSE parser, markdown chat & sidebar | ✅ **Completed** |
| **Phase 4** | **Conversation History & Context Engine** | `conversation_summaries`, sliding window, token budgeting, Context Engine | ✅ **Completed** |
| **Phase 5** | **Long-Term Memory & Hybrid Retrieval** | `memories` table, structured fact extraction + pgvector cosine similarity | ✅ **Completed** |
| **Phase 6** | **Tool Registry & Permission Guardrails** | Centralized tool registry, safety classification (read-only vs dangerous) | 🔄 **Next Up** |
| **Phase 7** | **Security & User Confirmations** | Guardrails requiring interactive user approval for destructive operations | 📋 Planned |
| **Phase 8** | **Knowledge Ingestion & pgvector RAG** | Document chunking, vector indexing, retrieval with grounded citations | 📋 Planned |
| **Phase 9** | **Planner & Autonomous Execution** | Progressive autonomy, multi-step planning loops, tool observation loop | 📋 Planned |
| **Phase 10** | **Production Hardening & Deployment** | Audit logs, benchmarks, rate limiting, and release packaging | 📋 Planned |

---

## 🔍 Detailed Phase Specifications

### ✅ Phase 1: FastAPI + Brain + Ollama Abstraction (Done)
- **Goal**: Establish pure local-first inference with zero external cloud dependencies.
- **Completed Deliverables**:
  - Abstract interface `LLMProvider` in `src/app/modules/brain/interfaces.py` defining `generate`, `stream_chat`, and `get_embedding`.
  - Concrete implementation `OllamaAdapter` in `src/app/infrastructure/ollama/adapter.py` connecting to `http://localhost:11434`.
  - Configurable model selection (`qwen2.5`, `qwen3`) via environment variables.
  - Docker container entrypoint fixed with `PYTHONPATH=/app/src` and live reload.

### ✅ Phase 2: Sessions + Messages Persistence (Done)
- **Goal**: Full conversation history persistence in PostgreSQL.
- **Completed Deliverables**:
  - SQLAlchemy Async models for `Session` and `Message` in `src/app/modules/sessions/models.py`.
  - Alembic migration `3ccc2be706bc_initial_schema` creating `sessions` and `messages` tables on port `5434`.
  - API endpoints: `POST /api/v1/sessions`, `GET /api/v1/sessions`, `GET /api/v1/sessions/{id}`, `DELETE /api/v1/sessions/{id}`.
  - Automatic persistence of user inputs and assistant streaming responses into database.

### ✅ Phase 3: Next.js + SSE Integration (Done)
- **Goal**: Premium, responsive web interface adhering to Feature-Architecture-Oriented System (FAOS).
- **Completed Deliverables**:
  - Scaffolding from `next-template-v1` configured on **Port 3008**.
  - Resilient SSE client in `src/shared/lib/sse.ts` supporting chunk buffering and `AbortController`.
  - Business features:
    - `features/chat`: `ChatContainer`, `ChatMessageList`, `ChatMessageBubble`, `ChatInput`, `StreamingCursor`, `useChatStream`.
    - `features/sessions`: `SessionSidebar`, `SessionListItem`, Server Actions in `src/app/actions/sessions.ts`.
  - Server Components with SSR session prefetching in `src/app/page.tsx` and `src/app/c/[sessionId]/page.tsx`.
  - Architecture verified with 0 lint warnings, 0 type errors, and clean Next.js production build.

---

### 🔄 Phase 4: Conversation History & Context Engine (Ready to Execute)

#### 1. Objectives
Instead of sending an unbounded array of raw messages to the model on every turn, the **Context Engine** selects and formats the optimal token package:
- **Token Budgeting**: Respect context windows (e.g. 8k, 32k) and allocate token budgets across system prompt, long-term memory, conversation summary, and recent messages.
- **Conversation Summarization**: Automatically compress older conversation turns into a rolling summary stored in PostgreSQL.
- **Sliding Message Window**: Keep the latest $K$ turns verbatim for precise conversational flow.

#### 2. Database Schema Additions
```sql
CREATE TABLE conversation_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    last_message_id UUID NOT NULL REFERENCES messages(id),
    tokens_count INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_conversation_summaries_session_id ON conversation_summaries(session_id);
```

#### 3. Code Implementation Steps
1. **Alembic Migration**:
   - Create `conversation_summaries` model in `src/app/modules/sessions/models.py`.
   - Generate and run Alembic migration for `conversation_summaries`.
2. **Context Engine Module (`src/app/modules/brain/context.py`)**:
   - Implement `ContextEngine` class.
   - Methods:
     - `get_relevant_summary(session_id: UUID) -> Optional[str]`
     - `get_recent_messages(session_id: UUID, limit: int = 10) -> List[Message]`
     - `assemble_prompt_context(session_id: UUID, current_input: str) -> List[Dict[str, str]]`
3. **Background Summarizer Service**:
   - When message count in a session exceeds a threshold (e.g. > 10 messages), trigger asynchronous summary generation using `LLMProvider`.
4. **Brain Orchestration Update (`src/app/modules/brain/orchestrator.py`)**:
   - Wire `ContextEngine` into `BrainOrchestrator.process_chat_stream`.

---

### 📋 Phase 5: Long-Term Memory & Hybrid Retrieval

#### 1. Objectives
Extract durable facts, user preferences, and project decisions from conversations and store them in structured form, augmented by pgvector for semantic retrieval.

#### 2. Database Schema
```sql
CREATE TABLE memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    source_session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
    category VARCHAR(50) NOT NULL, -- 'preference', 'project', 'decision', 'goal'
    subject VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    importance VARCHAR(20) DEFAULT 'medium', -- 'low', 'medium', 'high', 'critical'
    confidence FLOAT DEFAULT 1.0,
    embedding vector(768), -- EmbeddingGemma or nomic-embed-text
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX idx_memories_category ON memories(category);
CREATE INDEX idx_memories_embedding ON memories USING hnsw (embedding vector_cosine_ops);
```

#### 3. Core Principles
- **Structured first**: Filter by user, project, category, and importance via SQL `WHERE`.
- **Vector search for semantic recall**: Cosine distance search over embeddings to discover relevant context when keywords differ.
- **Selective extraction**: Only write to memory when the user explicitly instructs ("Remember that...") or when high-confidence durable information is detected.

---

### 📋 Phase 6: Tool Registry & Permission Guardrails

#### 1. Objectives
Allow Sovereign to interact with its local environment (files, git, web search) while maintaining strict safety boundaries.

#### 2. Classification Matrix
- **READ-ONLY (Auto-Approved)**:
  - File reading (`read_file`, `list_dir`, `grep_search`)
  - Project inspection (`git status`, `git log`)
  - Web search (local documentation or allowed query)
- **LOW-RISK (Auto-Approved / Notified)**:
  - Draft creation in scratch directory
  - Temporary data generation
- **CONFIRMATION REQUIRED (Explicit User Consent)**:
  - File modifications / writes
  - File deletions
  - Git commits / pushes
  - Destructive SQL queries (`DROP`, `TRUNCATE`, bulk `DELETE`)

#### 3. Architecture
```text
Brain Tool Call Request
       │
       ▼
Permission Guard
       │
   Is action safe?
   ├── YES ──► Execute Tool ──► Feed Result to Brain
   └── NO  ──► Emit SSE 'confirmation_required' event
                     │
                     ▼
               Wait for User Action in UI (Approve / Deny)
```

---

### 📋 Phase 7: Security & Interactive UI Confirmations
- Next.js UI modal/inline widget rendering interactive approval cards for pending tool calls.
- FastAPI confirmation endpoint: `POST /api/v1/tools/confirm/{execution_id}` with decision (`approved` / `rejected`).
- Backend audit log table: `tool_executions` recording every invocation, arguments, approver, status, and output.

---

### 📋 Phase 8: Knowledge Ingestion & pgvector RAG
- Document parsing for Markdown, PDF, text, and code files.
- Chunking strategy (recursive text splitting, token-aware chunks with header preservation).
- Vector embeddings generated via local Ollama (`embeddinggemma` or `nomic-embed-text`).
- Storage in `knowledge_documents` and `knowledge_chunks` tables with HNSW index.
- Context injection into Context Engine with explicit file citations.

---

### 📋 Phase 9: Planner & Autonomous Multi-Step Execution
- Implementation of progressive autonomy:
  - **Level 0 (Direct)**: Direct answer for simple Q&A.
  - **Level 1 (Tool-Assisted)**: Single tool invocation (e.g. read a file and summarize).
  - **Level 2 (Multi-Step Planner)**: Complex tasks decomposed into plan steps, executed iteratively with intermediate observations.
- Python-native control loop:
  `Plan -> Step -> Tool -> Observe -> Reflect -> Next Step -> Final Synthesis`.

---

### 📋 Phase 10: Production Hardening & Deployment
- Rate limiting and local resource monitoring (GPU/VRAM/CPU tracking for Ollama).
- Test suites: automated unit tests for Context Engine, Tool Guard, and API contracts.
- System metrics and latency instrumentation.
- Single-command start scripts (`start-sovereign.ps1` / `docker-compose.prod.yml`).

---

## 🔒 Non-Negotiable Engineering Rules
1. **Local-First Only**: Zero external cloud API keys (no OpenAI, no Anthropic, no Gemini, no OpenRouter).
2. **Git Attribution**: All commits must be authored strictly by `Reign Mark Valdez <valdezreignmark@gmail.com>`. **NO `Co-authored-by:` or AI signatures**.
3. **No Third-Party Agent Frameworks**: No LangChain, no LlamaIndex, no CrewAI, no OpenClaw runtime. The cognitive engine is native Python.
4. **Simple Requests Stay Simple**: Do not activate planner or tools unless the request necessitates multi-step execution.
