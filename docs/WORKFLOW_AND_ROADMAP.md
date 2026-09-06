# Project Sovereign — Recommended Architecture & Roadmap

## Core Recommendation

Project Sovereign treats **Conversation History, Long-Term Memory, Knowledge/RAG, Tools, and Planning as separate but connected capabilities**.

The system does not rely entirely on vector search, nor does it rely entirely on database categorization.

The architecture is a **hybrid engine**:

* **PostgreSQL structured data** → source of truth, organization, filtering, relationships, and application state.
* **pgvector embeddings** → semantic discovery and similarity retrieval.
* **Conversation history** → complete record of what the user and Sovereign discussed.
* **Conversation summaries** → compressed context for long conversations.
* **Long-term memory** → curated durable information extracted from conversations.
* **Knowledge/RAG** → project documents and external knowledge.
* **Tool Registry** → controlled capabilities Sovereign can execute.
* **Planner** → multi-step reasoning and task execution.

---

## 🏛️ System Architecture

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

As the application scales, Next.js will evolve into a **Backend-For-Frontend (BFF)** layer equipped with **Prisma** for direct application state and database access:

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

## 1. Conversation History — Save Everything

Conversation history works like any modern AI application: every conversation is persisted.

```text
User
  ↓
Session / Conversation
  ↓
Messages
  ├── user messages
  ├── assistant messages
  ├── tool calls
  ├── tool results
  └── metadata
```

Conversation history answers: **"What did we talk about?"**
History is **never** replaced by long-term memory. The original messages remain the authoritative record.

---

## 2. Conversation Context Management

The entire conversation is not sent to Ollama on every request. For short conversations, recent messages are passed directly. For long conversations, Sovereign assembles context dynamically:

```text
Conversation Summary
        +
Recent Messages
        +
Relevant Older Messages
        +
Relevant Long-Term Memories
        +
Relevant Knowledge
        ↓
     Context
        ↓
      Ollama
```

This ensures continuity while preserving context limits and local inference speed.

---

## 3. Long-Term Memory — Curated, Not Everything

Long-term memory contains durable information intentionally extracted from conversations:
* User preferences
* Long-term goals
* Project information
* Technical decisions
* Recurring workflows
* Important recurring context
* Explicitly requested memories

Do **not** blindly convert every message into memory.

### Recommended Memory Structure:
```text
memory
├── id
├── user_id
├── category
├── subject
├── content
├── importance
├── confidence
├── source_session_id
├── created_at
└── updated_at
```

---

## 4. Structured Categorization + Vector Search (Hybrid)

Project Sovereign uses **both** structured categorization and vector embeddings.

- **Structured data is used for**: Exact filtering, categories, user/project relationships, permissions, dates, importance, confidence, session relationships, application state.
- **Vector data is used for**: Semantic similarity, finding related conversations, finding relevant memories, retrieving relevant document chunks, discovering information across variations in user phrasing.

---

## 5. Hybrid Retrieval Flow

```text
                    User Request
                         ↓
                  Context Retrieval
                         │
              ┌──────────┴──────────┐
              │                     │
       Structured Search       Vector Search
              │                     │
       Categories / IDs        Semantic similarity
       Project / Session       Related concepts
       Date / Importance       Related discussions
              │                     │
              └──────────┬──────────┘
                         ↓
                  Context Ranking
                         ↓
                      Ollama
```

The structured database provides **control and precision**.
The vector layer provides **semantic discovery**.

---

## 6. Separate Persistent Data Types

```text
PostgreSQL
│
├── users
├── sessions
├── messages
├── conversation_summaries
├── memories
├── knowledge_documents
├── knowledge_chunks
└── tool_executions
```

Target vector embeddings with pgvector:
* `conversation_summaries` → useful
* `memories` → useful
* `knowledge_chunks` → essential
* `selected messages` → optional

---

## 7. Separation of Responsibilities

* **Conversation History**: *"What happened?"* — Complete record of the conversation.
* **Long-Term Memory**: *"What should Sovereign remember?"* — Curated durable information.
* **Knowledge / RAG**: *"What information exists in the knowledge base?"* — Documents, files, technical references.
* **Tools**: *"What can Sovereign do?"* — Filesystem, web, Git, database, shell, and other controlled capabilities.
* **Planner**: *"How should Sovereign accomplish this complex task?"* — Multi-step planning and execution.

---

## 8. Phased Implementation Roadmap

| Phase | System | Status |
| :--- | :--- | :---: |
| **Phase 1** | FastAPI + Brain + Ollama Abstraction | ✅ Done |
| **Phase 2** | Sessions + Messages Persistence | ✅ Done |
| **Phase 3** | Next.js + SSE Integration | ✅ Done |
| **Phase 4** | **Conversation History + Context Management** | 🔄 Next |
| **Phase 5** | **Long-Term Memory + Hybrid Retrieval** | 🔄 |
| **Phase 6** | **Tool Registry + Permission Guardrails** | 🔄 |
| **Phase 7** | **Security + User Confirmations** | 🔄 |
| **Phase 8** | **Knowledge Ingestion + pgvector RAG** | 🔄 |
| **Phase 9** | **Planner + Multi-Step Execution** | 🔄 |
| **Phase 10** | **Production Hardening + Deployment** | 🔄 |

---

## 9. Cognitive Workflow (The Autonomous Agent Loop)

```text
                         USER
                           │
                           ▼
                    SOVEREIGN BRAIN
                           │
                           ▼
                   Understand Request
                           │
                           ▼
                   Build Task Context
                           │
          ┌────────────────┼─────────────────┐
          │                │                 │
          ▼                ▼                 ▼
   Conversation        Long-Term         Knowledge
      History            Memory              RAG
          │                │                 │
          └────────────────┼─────────────────┘
                           ▼
                    Context Assembly
                           │
                           ▼
                    Decision / Planner
                           │
              ┌────────────┼─────────────┐
              │            │             │
              ▼            ▼             ▼
            Answer      Retrieve       Tool
                                      Call
                                        │
                                        ▼
                                Permission Guard
                                        │
                              ┌─────────┴─────────┐
                              │                   │
                         Auto-approved      Confirmation
                              │                   │
                              └─────────┬─────────┘
                                        ▼
                                  Execute Tool
                                        │
                                        ▼
                                  Observe Result
                                        │
                                        ▼
                                  Brain Evaluates
                                        │
                              ┌─────────┴─────────┐
                              ▼                   ▼
                           Continue            Finish
                                                  │
                                                  ▼
                                             Save History
                                                  │
                                                  ▼
                                      Extract Memory if needed
```

---

## 10. Golden Rule

> **Store everything as history, remember selectively, retrieve intelligently, and authorize every capability.**

- **Simple requests stay simple**:
  `User ➔ Relevant Context ➔ Ollama ➔ Answer`
- **Complex tasks scale progressively**:
  `User ➔ Context ➔ Planner ➔ Tools ➔ Permission ➔ Execution ➔ Observation ➔ Reasoning ➔ Final Answer`
