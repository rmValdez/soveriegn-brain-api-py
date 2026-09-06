# Project Sovereign — Next.js Monolith Architecture & Migration Plan

> **Persistent Blueprint for Sovereign Cognitive Platform**
>
> **Architecture Direction:** Next.js Monolith + PostgreSQL/pgvector + Ollama
>
> **Migration Strategy:** Incremental migration from the existing FastAPI Brain
>
> **Principle:** Preserve completed work while progressively moving the cognitive engine into the Next.js monolith.

---

# 🏛️ Target System Architecture

```text
                              ┌──────────────────────┐
                              │       Browser        │
                              │    React / Next.js    │
                              └──────────┬───────────┘
                                         │
                                         ▼
              ┌──────────────────────────────────────────────┐
              │              NEXT.JS MONOLITH                │
              │                   :3008                      │
              │                                              │
              │ ┌──────────────────────────────────────────┐ │
              │ │ Presentation Layer                       │ │
              │ │ • React / App Router                     │ │
              │ │ • Server Components                       │ │
              │ │ • Client Components                       │ │
              │ │ • Zustand UI State                        │ │
              │ │ • Streaming Chat UI                       │ │
              │ └──────────────────────────────────────────┘ │
              │                                              │
              │ ┌──────────────────────────────────────────┐ │
              │ │ Application / BFF Layer                  │ │
              │ │ • Route Handlers                           │ │
              │ │ • Server Actions                           │ │
              │ │ • Authentication                           │ │
              │ │ • User Preferences                         │ │
              │ │ • Session Metadata                         │ │
              │ │ • Audit State                              │ │
              │ └──────────────────────────────────────────┘ │
              │                                              │
              │ ┌──────────────────────────────────────────┐ │
              │ │ Sovereign Cognitive Engine               │ │
              │ │ • LLM Provider                             │ │
              │ │ • Ollama Adapter                           │ │
              │ │ • Context Engine                           │ │
              │ │ • Conversation Summarizer                  │ │
              │ │ • Long-Term Memory                         │ │
              │ │ • Hybrid Retrieval / RAG                   │ │
              │ │ • Tool Registry                            │ │
              │ │ • Permission Guard                         │ │
              │ │ • Confirmation Manager                     │ │
              │ │ • Planner                                  │ │
              │ │ • Agent Execution Loop                     │ │
              │ └──────────────────────────────────────────┘ │
              │                                              │
              │ ┌──────────────────────────────────────────┐ │
              │ │ Data Access Layer                         │ │
              │ │ • Prisma ORM                               │ │
              │ │ • PostgreSQL Client                        │ │
              │ │ • pgvector                                 │ │
              │ └──────────────────────────────────────────┘ │
              └───────────────────────┬──────────────────────┘
                                      │
                    ┌─────────────────┴──────────────────┐
                    │                                    │
                    ▼                                    ▼
          ┌────────────────────┐              ┌────────────────────┐
          │ PostgreSQL         │              │ Ollama             │
          │ + pgvector         │              │ :11434             │
          │                    │              │                    │
          │ Users              │              │ Qwen                │
          │ Sessions           │              │ Qwen Coder          │
          │ Messages           │              │ EmbeddingGemma      │
          │ Summaries          │              │ Other local models  │
          │ Memories           │              └────────────────────┘
          │ Knowledge          │
          │ Tool Executions    │
          │ Audit Logs         │
          └────────────────────┘
```

---

# 🎯 Core Architectural Decision

Project Sovereign will ultimately operate as a **Next.js monolith**.

Next.js becomes the primary application and cognitive runtime.

FastAPI is treated as a **migration-stage component**, not a permanent architectural dependency.

The final runtime should not require:

```text
Next.js → FastAPI → Ollama
```

Instead:

```text
Next.js
   ├── Application
   ├── BFF
   ├── Cognitive Engine
   ├── Memory
   ├── RAG
   ├── Tools
   ├── Planner
   └── Ollama Adapter
          │
          ▼
       Ollama
```

---

# 🔄 Migration Strategy

Do NOT rewrite the entire system at once.

Existing completed functionality must be preserved and migrated incrementally.

## Current Architecture

```text
Browser
   ↓
Next.js :3008
   ↓ HTTP / SSE
FastAPI :3009
   ↓
Ollama :11434
   ↓
PostgreSQL :5434
```

## Transitional Architecture

```text
Browser
   ↓
Next.js Monolith
   │
   ├── New BFF / Prisma Layer
   │
   ├── Migrated Cognitive Modules
   │
   └── Temporary FastAPI Bridge
              ↓
           Ollama
```

During migration, Next.js may communicate with FastAPI only for functionality that has not yet been migrated.

## Final Architecture

```text
Browser
   ↓
Next.js Monolith
   │
   ├── UI
   ├── BFF
   ├── Authentication
   ├── Sessions
   ├── Context Engine
   ├── Memory
   ├── RAG
   ├── Tools
   ├── Permission Guard
   ├── Planner
   ├── LLM Provider
   └── Ollama Adapter
          │
          ├── PostgreSQL + pgvector
          └── Ollama
```

---

# 📊 Revised Roadmap

| Phase | Subsystem | Key Deliverables | Status |
| :---: | :--- | :--- | :---: |
| **Phase 1** | **FastAPI + Brain + Ollama Abstraction** | Abstract `LLMProvider`, `OllamaAdapter`, Docker Compose (:3009, :5434) | ✅ Completed |
| **Phase 2** | **Sessions + Messages Persistence** | SQLAlchemy 2.0 Async, Alembic migrations, CRUD API routes | ✅ Completed |
| **Phase 3** | **Next.js + SSE Client UI** | Next.js 15 FAOS App Router (:3008), SSE parser, markdown chat & sidebar | ✅ Completed |
| **Phase 4** | **Conversation History + Context Engine** | `conversation_summaries`, sliding window, token budgeting, Context Engine | ✅ Completed |
| **Phase 5** | **Long-Term Memory + Hybrid Retrieval** | `memories` table, structured fact extraction + pgvector cosine similarity | ✅ Completed |
| **Phase 6** | **Tool Registry + Permission Guardrails** | Centralized tool registry, safety classification (read-only vs dangerous) | ✅ Completed |
| **Phase 7** | **Security + Interactive Confirmations** | Guardrails requiring interactive user approval for destructive operations | 🔄 **Next Up** |
| **Phase 7B** | **Next.js BFF + Prisma Layer** | Prisma ORM in Next.js for User Accounts, Preferences, and Audit State | 🔄 **Migration Foundation** |
| **Phase 8** | **Knowledge Ingestion + RAG** | Document chunking, vector indexing, retrieval with grounded citations | 📋 Planned |
| **Phase 9** | **Planner + Autonomous Execution** | Progressive autonomy, multi-step planning loops, tool observation loop | 📋 Planned |
| **Phase 10** | **Cognitive Engine Migration to Next.js** | Native TypeScript ContextEngine, Memory, Tools, and Ollama adapter | 📋 Planned |
| **Phase 11** | **FastAPI Retirement** | Decommission temporary Python bridge once Next.js handles all cognitive tasks | 📋 Planned |
| **Phase 12** | **Production Hardening + Deployment** | Audit logs, benchmarks, rate limiting, and single-command startup | 📋 Planned |

---

# 🧠 Cognitive Engine Target Structure

The cognitive engine should become a native module inside Next.js.

Recommended structure:

```text
src/
├── app/
│   ├── api/
│   │   ├── chat/
│   │   ├── sessions/
│   │   ├── tools/
│   │   ├── memory/
│   │   └── knowledge/
│   │
│   ├── actions/
│   └── ...
│
├── features/
│   ├── chat/
│   ├── sessions/
│   ├── memory/
│   ├── knowledge/
│   └── tools/
│
├── server/
│   ├── brain/
│   │   ├── orchestrator.ts
│   │   ├── context.ts
│   │   ├── summarizer.ts
│   │   ├── planner.ts
│   │   ├── memory.ts
│   │   └── types.ts
│   │
│   ├── llm/
│   │   ├── provider.ts
│   │   ├── ollama.ts
│   │   └── model-router.ts
│   │
│   ├── tools/
│   │   ├── registry.ts
│   │   ├── permissions.ts
│   │   ├── executor.ts
│   │   └── confirmations.ts
│   │
│   ├── rag/
│   │   ├── ingestion.ts
│   │   ├── chunking.ts
│   │   ├── embeddings.ts
│   │   └── retrieval.ts
│   │
│   └── db/
│       └── prisma.ts
│
├── shared/
│   ├── lib/
│   ├── types/
│   └── utils/
│
└── prisma/
    └── schema.prisma
```

---

# 🤖 LLM Abstraction

The cognitive engine must not depend directly on Qwen.

Create a provider abstraction:

```text
LLMProvider
    │
    ├── generate()
    ├── streamChat()
    └── getEmbedding()
```

Implementation:

```text
LLMProvider
      │
      ▼
Model Router
      │
 ┌────┼───────────────┐
 ▼    ▼               ▼
Qwen  Qwen Coder      Other Local Models
```

Ollama remains the local inference gateway.

This allows Sovereign to change models without changing the cognitive engine.

---

# 🔀 Model Routing

Sovereign should eventually support automatic model selection.

Example:

```text
User Request
      │
      ▼
Model Router
      │
      ├── Simple conversation
      │       ↓
      │     Small Qwen
      │
      ├── Programming
      │       ↓
      │     Qwen Coder
      │
      ├── Complex reasoning
      │       ↓
      │     Larger local model
      │
      └── Embeddings
              ↓
         EmbeddingGemma
```

The user should also be able to manually select a model from the UI.

---

# 🧠 Context Engine

The Context Engine remains responsible for constructing the optimal context package.

```text
Current User Input
       │
       ▼
Context Engine
       │
       ├── System Instructions
       ├── Relevant Long-Term Memories
       ├── Conversation Summary
       ├── Recent Messages
       ├── Retrieved Knowledge
       └── Tool Results
       │
       ▼
LLM Provider
```

Context should be token-budgeted.

Do not blindly send the entire conversation history.

---

# 💾 Memory Architecture

Memory remains separate from conversation history.

```text
Conversation
     │
     ▼
Memory Extraction
     │
     ├── Preference
     ├── Project
     ├── Decision
     └── Goal
     │
     ▼
Structured Memory
     │
     ▼
Embedding
     │
     ▼
pgvector
```

Memory retrieval should combine:

```text
SQL filtering
      +
semantic vector search
```

Structured filtering must happen before or alongside vector retrieval.

---

# 📚 Knowledge / RAG

Knowledge remains separate from personal memory.

```text
Documents
   │
   ▼
Parser
   │
   ▼
Chunker
   │
   ▼
Embedding
   │
   ▼
PostgreSQL + pgvector
   │
   ▼
Semantic Retrieval
   │
   ▼
Context Engine
```

Supported sources:

```text
Markdown
PDF
TXT
Code
Documentation
Project files
```

Retrieved knowledge should provide explicit source/file citations.

---

# 🛠️ Tool Architecture

Tools are registered through a native tool registry.

```text
Brain
  │
  ▼
Tool Registry
  │
  ▼
Permission Guard
  │
  ├── Safe
  │    ↓
  │  Execute
  │
  └── Requires Confirmation
       ↓
    UI Confirmation
       ↓
    Approve / Reject
       ↓
    Execute / Cancel
```

No third-party agent framework should be introduced.

Do not use:

```text
LangChain
LlamaIndex
CrewAI
OpenClaw runtime
```

The orchestration system remains native to Sovereign.

---

# 🔐 Permission Model

## READ-ONLY

Automatically approved:

```text
read_file
list_dir
grep_search
git status
git log
safe web search
```

## LOW-RISK

Automatically approved or notified:

```text
temporary files
scratch files
temporary generated data
```

## CONFIRMATION REQUIRED

Explicit user approval:

```text
file writes
file modifications
file deletion
git commit
git push
destructive SQL
bulk DELETE
DROP
TRUNCATE
```

---

# 🧩 Planner

The planner should only activate when necessary.

```text
User Request
      │
      ▼
Complexity Check
      │
      ├── Simple
      │      ↓
      │   Direct Answer
      │
      ├── Single Tool
      │      ↓
      │   Tool Execution
      │
      └── Complex
             ↓
          Planner
             ↓
           Plan
             ↓
           Step
             ↓
           Tool
             ↓
         Observe
             ↓
          Reflect
             ↓
        Next Step
             ↓
       Final Synthesis
```

Simple requests must remain simple.

Do not invoke the planner unnecessarily.

---

# 🗄️ Database Ownership

PostgreSQL remains the central persistence layer.

Prisma should become the primary database access layer for the Next.js monolith.

Core data domains:

```text
User
UserPreference
Session
SessionMetadata
Message
ConversationSummary
Memory
KnowledgeDocument
KnowledgeChunk
ToolExecution
AuditLog
```

pgvector remains responsible for semantic retrieval.

---

# 🐍 FastAPI Migration

FastAPI should be migrated module-by-module.

Recommended migration order:

```text
1. LLM Provider
       ↓
2. Ollama Adapter
       ↓
3. Context Engine
       ↓
4. Conversation Summarizer
       ↓
5. Memory
       ↓
6. RAG
       ↓
7. Tool Registry
       ↓
8. Permission Guard
       ↓
9. Planner
       ↓
10. Brain Orchestrator
```

After each migration:

```text
Test
 ↓
Compare behavior
 ↓
Switch Next.js to new implementation
 ↓
Remove old FastAPI dependency
```

Only retire FastAPI once all cognitive responsibilities have been successfully migrated.

---

# 🚫 Final Architecture Constraint

FastAPI must NOT become a permanent mandatory dependency simply because the initial implementation used Python.

The target is:

```text
                    PROJECT SOVEREIGN
                           │
                           ▼
                    NEXT.JS MONOLITH
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
       Prisma          Cognitive         UI/BFF
          │              Engine
          │                │
          │        ┌───────┼────────┐
          │        │       │        │
          ▼        ▼       ▼        ▼
     PostgreSQL  Memory   RAG     Tools
          │
          └────────── pgvector
                           
                           │
                           ▼
                         Ollama
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
            Qwen       Qwen Coder   Embedding
```

---

# 🔒 Non-Negotiable Engineering Rules

1. **Local-First Only**
   * No OpenAI API.
   * No Anthropic API.
   * No Gemini API.
   * No OpenRouter.
   * Ollama is the local inference gateway.

2. **Native Cognitive Engine**
   * No LangChain.
   * No LlamaIndex.
   * No CrewAI.
   * No OpenClaw runtime.
   * Implement orchestration natively.

3. **Next.js Monolith**
   * Next.js is the long-term application and cognitive runtime.
   * FastAPI is transitional only.

4. **Database Discipline**
   * PostgreSQL is the primary persistence layer.
   * Prisma is the primary Next.js ORM.
   * pgvector handles semantic retrieval.

5. **Simple Requests Stay Simple**
   * Do not activate tools or planning unless required.

6. **Security by Default**
   * Destructive operations require explicit confirmation.
   * Every tool execution is auditable.

7. **Incremental Migration**
   * Do not rewrite working functionality unnecessarily.
   * Preserve existing Phase 1–6 functionality.
   * Migrate one subsystem at a time.

8. **Git Attribution**
   * All commits must be authored strictly by:
     `Reign Mark Valdez <valdezreignmark@gmail.com>`
   * No `Co-authored-by:` lines.
   * No AI signatures.

---

# 🏁 Final Vision

Project Sovereign is not intended to be merely a chatbot UI around Qwen.

It is intended to become a **local-first cognitive platform** where the model is only one component of a larger system:

```text
                 SOVEREIGN
                     │
       ┌─────────────┼─────────────┐
       ▼             ▼             ▼
    Memory          RAG          Tools
       │             │             │
       └─────────────┼─────────────┘
                     ▼
                  Context
                     │
                     ▼
                  Planner
                     │
                     ▼
               Model Router
                     │
          ┌──────────┼──────────┐
          ▼          ▼          ▼
        Qwen      Qwen Coder   Other
          │
          ▼
        Ollama
```

The ultimate goal is:

> **One Next.js monolith containing the Sovereign application, cognitive engine, memory, RAG, tools, planner, security layer, and model orchestration — backed by PostgreSQL/pgvector and local Ollama inference.**

FastAPI is the bridge that helped build the system.

**Next.js becomes the destination.**
