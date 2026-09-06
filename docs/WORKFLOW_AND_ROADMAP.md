# Project Sovereign — Final Architecture, Workflow & Implementation Roadmap

## Core Recommendation

Project Sovereign should be built as a **local-first, context-aware AI agent platform**, not merely as an Ollama chat interface.

The architecture separates five major capabilities while allowing them to work together:

1. **Conversation History** — everything the user and Sovereign discussed.
2. **Long-Term Memory** — durable information worth remembering.
3. **Knowledge / RAG** — information contained in documents and knowledge sources.
4. **Tools** — capabilities Sovereign is authorized to execute.
5. **Planning** — the ability to solve complex tasks through multiple steps.

The recommended architecture is a **hybrid engine**:

* **PostgreSQL** → source of truth, structured data, relationships, filtering, and application state.
* **pgvector** → semantic discovery and similarity retrieval where useful.
* **Conversation History** → complete authoritative record of conversations.
* **Conversation Summaries** → compressed context for long conversations.
* **Long-Term Memory** → curated durable information extracted from conversations.
* **Knowledge / RAG** → project documents and indexed knowledge.
* **Tool Registry + Permissions** → controlled capabilities Sovereign can execute.
* **Planner** → multi-step task execution.
* **Next.js Monolith + BFF** → application, UI, authentication, session management, and frontend-facing backend responsibilities.
* **FastAPI Sovereign Brain** → dedicated cognitive and agent execution engine.

### Golden Rule

> **Store everything as history, remember selectively, retrieve intelligently, manage context deliberately, authorize every capability, keep simple requests simple, and scale autonomy only when the task requires it.**

---

# 1. System Architecture

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
                         │ • React / UI                   │
                         │ • Server Components             │
                         │ • Client Components             │
                         │ • Server Actions                │
                         │ • API Routes                    │
                         │ • Authentication                │
                         │ • User Preferences              │
                         │ • Session Metadata              │
                         │ • Prisma                         │
                         │ • Application State              │
                         │ • UI Cache / Revalidation        │
                         │ • SSE Proxy                      │
                         └───────────────┬────────────────┘
                                         │
                                  HTTP / SSE
                                         │
                                         ▼
                         ┌────────────────────────────────┐
                         │          FASTAPI                 │
                         │       SOVEREIGN BRAIN            │
                         │                                │
                         │ • Brain Orchestration            │
                         │ • Context Engine                 │
                         │ • Long-Term Memory               │
                         │ • Knowledge / RAG                │
                         │ • Tool Registry                  │
                         │ • Permission System              │
                         │ • Planner                        │
                         │ • Agent Execution Loop           │
                         │ • LLM Provider                   │
                         └───────────────┬────────────────┘
                                         │
                                  LLMProvider
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
                         │ Knowledge               │
                         │ Tool Executions         │
                         │ Vector Embeddings       │
                         └─────────────────────────┘
```

---

# 2. Next.js Monolith + BFF

Next.js should operate as the **application monolith and Backend-for-Frontend (BFF)**.

This does not mean putting the Sovereign Brain inside Next.js.

Instead, Next.js owns everything related to the application and user-facing experience.

### Next.js responsibilities

* React UI
* Server Components
* Client Components
* Server Actions
* API Routes
* Authentication
* User accounts
* User preferences
* Application settings
* Session metadata
* Application state
* Prisma
* UI caching
* Cache revalidation
* Frontend-facing APIs
* SSE proxying to FastAPI

Next.js should provide a unified application boundary instead of prematurely splitting the frontend into multiple services.

### FastAPI responsibilities

FastAPI remains the dedicated **Sovereign Brain**.

It owns:

* AI orchestration
* Context Engine
* Long-term memory
* Knowledge retrieval
* pgvector search
* Tool Registry
* Permission enforcement
* Planner
* Agent loops
* Tool execution
* Ollama model dispatch

### Architectural principle

> **Next.js is the application monolith. FastAPI is the intelligence engine.**

This gives the project a simple application architecture while preserving a clean boundary around AI and autonomous execution.

---

# 3. Conversation History — Store Everything

Conversation history should behave like a modern AI application.

Every conversation should be persisted.

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

Conversation history answers:

> **"What did we talk about?"**

The original messages remain the authoritative record.

Long-term memory must **never replace conversation history**.

If the user returns to a conversation days or months later, Sovereign should be able to reconstruct the relevant context from the persisted conversation.

---

# 4. Conversation Context Management

The entire conversation should not automatically be sent to Ollama on every request.

For short conversations:

```text
Recent Messages
      ↓
    Ollama
```

For long conversations:

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
   Context Engine
        ↓
   Context Ranking
        ↓
      Ollama
```

This provides continuity while controlling:

* Context size
* Token usage
* Local inference latency
* Memory consumption

---

# 5. Context Engine

The Context Engine is the subsystem responsible for deciding:

> **"Given the user's current request, what information from everything Sovereign knows is relevant right now?"**

```text
Sovereign Brain
      │
      ▼
┌────────────────────────┐
│     Context Engine     │
│                        │
│ Recent messages        │
│ Conversation summaries │
│ Older history          │
│ Long-term memory       │
│ Knowledge / RAG        │
│ Structured filters     │
│ Semantic retrieval     │
│ Context ranking        │
│ Token budgeting        │
└───────────┬────────────┘
            │
            ▼
          Ollama
```

The Context Engine should eventually handle:

* Retrieval
* Ranking
* Relevance
* Deduplication
* Context prioritization
* Token budgeting
* Context compression

This prevents the Sovereign Brain from becoming overloaded with retrieval-specific logic.

---

# 6. Long-Term Memory — Remember Selectively

Long-term memory contains durable information intentionally extracted from conversations.

Examples:

* User preferences
* Long-term goals
* Project information
* Technical decisions
* Recurring workflows
* Important recurring context
* Explicitly requested memories

Do **not** blindly convert every message into memory.

Example:

```text
Conversation:

"I'm building Project Sovereign using Next.js and FastAPI."

        ↓

Memory:

category = project
subject = Project Sovereign
content = "Project Sovereign uses Next.js and FastAPI."
importance = high
```

### Recommended memory structure

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

Memory should remain structured first and optionally vectorized for semantic retrieval.

---

# 7. Hybrid Retrieval — Structured + Vector

Project Sovereign should use **both structured categorization and vector embeddings**.

Do not make everything vector data.

### Structured PostgreSQL data

Used for:

* Exact filtering
* Categories
* User/project relationships
* Session relationships
* Dates
* Importance
* Confidence
* Application state
* Permissions
* Ownership

### pgvector

Used for:

* Semantic similarity
* Related conversations
* Relevant memories
* Similar technical decisions
* Document retrieval
* Discovering information despite different wording

Example:

```text
User:

"How did we decide the AI should handle filesystem operations?"

        ↓

Structured Retrieval

category = technical_decision
project = Project Sovereign

        +

Vector Retrieval

filesystem
tool permissions
sandboxing
confirmation
agent authority

        ↓

Context Ranking
        ↓
Ollama
```

Structured retrieval provides **precision**.

Vector retrieval provides **semantic discovery**.

Together they provide stronger retrieval than either approach alone.

---

# 8. Do Not Vectorize Everything

PostgreSQL remains the source of truth.

Recommended data structure:

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

Recommended vector usage:

```text
conversation_summaries → Vector: Useful
memories                → Vector: Useful
knowledge_chunks        → Vector: Essential
selected messages       → Vector: Optional
permissions             → Vector: No
session metadata        → Vector: No
application state       → Vector: No
```

The vector layer should enhance retrieval, not become the database itself.

---

# 9. Conversation History vs Memory vs Knowledge

These systems must remain conceptually separate.

### Conversation History

> **"What happened?"**

The complete record of the user's conversations.

### Long-Term Memory

> **"What should Sovereign remember?"**

Curated durable information extracted from conversations.

### Knowledge / RAG

> **"What information exists in the knowledge base?"**

Documents, project files, technical references, and indexed information.

### Tools

> **"What can Sovereign do?"**

Filesystem, web, Git, database, shell, and other controlled capabilities.

### Planner

> **"How should Sovereign accomplish this complex task?"**

Multi-step planning and execution.

---

# 10. Tool Registry

Tools should be centrally registered and controlled.

```text
modules/
└── tools/
    ├── registry.py
    ├── permissions.py
    ├── filesystem/
    ├── web/
    ├── git/
    ├── shell/
    └── database/
```

The LLM should **never directly own system authority**.

Instead:

```text
Brain
 ↓
Tool Selection
 ↓
Permission Guard
 ↓
Confirmation?
 ├── No → Execute
 └── Yes → Ask User
              ↓
           Execute
 ↓
Observe Result
 ↓
Brain
```

Python/backend enforcement remains the final authority.

---

# 11. Security and Confirmation

Security should be implemented **before full autonomous execution**.

Once tools exist, permissions and confirmations must already exist.

Recommended classification:

```text
READ-ONLY
├── read files
├── inspect project
├── search knowledge
└── web search

LOW-RISK
├── create draft
├── generate file
└── analyze data

CONFIRMATION REQUIRED
├── modify files
├── delete files
├── git commit
├── git push
├── deploy
└── destructive database operations
```

The model can request an action.

The model cannot authorize itself.

---

# 12. Knowledge / RAG

Knowledge is separate from memory.

Knowledge ingestion should support:

```text
Document
 ↓
Extraction
 ↓
Cleaning
 ↓
Chunking
 ↓
Embedding
 ↓
pgvector
 ↓
Semantic Retrieval
 ↓
Context Engine
 ↓
Ollama
```

Knowledge chunks should contain enough metadata for structured filtering:

```text
knowledge_chunk
├── id
├── document_id
├── content
├── embedding
├── source
├── category
├── metadata
├── created_at
└── updated_at
```

---

# 13. Planner — Progressive Autonomy

The planner should only activate when the task actually requires it.

### Simple request

```text
User
 ↓
Relevant Context
 ↓
Ollama
 ↓
Answer
```

### Complex task

```text
User
 ↓
Context
 ↓
Planner
 ↓
Step 1
 ↓
Tool
 ↓
Observe
 ↓
Step 2
 ↓
Tool
 ↓
Observe
 ↓
Reason
 ↓
Final Answer
```

This preserves the principle:

> **Simple Requests Stay Simple.**

Sovereign should not invoke a planner, tools, RAG, or unnecessary memory retrieval for a basic question when a direct answer is sufficient.

---

# 14. Autonomous Agent Loop

The final cognitive workflow should be:

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
                           ▼
                    CONTEXT ENGINE
                           │
          ┌────────────────┼─────────────────┐
          │                │                 │
          ▼                ▼                 ▼
   Conversation       Long-Term         Knowledge
      History            Memory             RAG
          │                │                 │
          └────────────────┼─────────────────┘
                           ▼
                  Context Ranking
                           │
                           ▼
                   Decision / Planner
                           │
              ┌────────────┼─────────────┐
              │            │             │
              ▼            ▼             ▼
            Answer      Retrieve        Tool
                                        Call
                                          │
                                          ▼
                                  Permission Guard
                                          │
                              ┌───────────┴───────────┐
                              │                       │
                         Auto-approved          Confirmation
                              │                       │
                              └───────────┬───────────┘
                                          ▼
                                    Execute Tool
                                          │
                                          ▼
                                    Observe Result
                                          │
                                          ▼
                                  Brain Evaluates
                                          │
                              ┌───────────┴───────────┐
                              ▼                       ▼
                           Continue                Finish
                                                      │
                                                      ▼
                                               Save History
                                                      │
                                                      ▼
                                          Extract Memory if needed
```

---

# 15. Persistence Model

PostgreSQL should act as the persistent foundation of Sovereign.

```text
PostgreSQL
│
├── users
│
├── sessions
│
├── messages
│
├── conversation_summaries
│
├── memories
│
├── knowledge_documents
│
├── knowledge_chunks
│
└── tool_executions
```

The key distinction is:

```text
Messages
    ↓
Complete historical record

Summaries
    ↓
Compressed conversation context

Memories
    ↓
Durable facts

Knowledge
    ↓
Indexed information

Tool Executions
    ↓
Action history / audit trail
```

---

# 16. Phased Implementation Roadmap

> **See `IMPLEMENTATION_PLAN.md` for the current, authoritative phase-status
> table.** This section previously kept its own copy, which drifted out of
> sync with the tracker in `IMPLEMENTATION_PLAN.md` (this doc had Phases
> 4-10 marked as not yet started, while the other doc had Phases 4-7 marked
> completed — both couldn't be right). Maintaining one tracker instead of
> duplicating it across docs is the fix.
>
> The recommended development order below (§17) is still accurate as
> architectural sequencing guidance, independent of what's actually shipped.

---

# 17. Recommended Development Order

The recommended implementation order is:

```text
Phase 1
FastAPI + Brain + Ollama
        ↓
Phase 2
Persistence
        ↓
Phase 3
Next.js + SSE
        ↓
Phase 4
Context Engine
        ↓
Phase 5
Long-Term Memory
        ↓
Phase 6
Tool Registry + Permissions
        ↓
Phase 7
Security + Confirmations
        ↓
Phase 8
Knowledge + RAG
        ↓
Phase 9
Planner + Autonomous Execution
        ↓
Phase 10
Production Hardening
```

The Context Engine should be established before the system becomes heavily dependent on memory, RAG, and autonomous planning.

---

# 18. Final Design Philosophy

Project Sovereign should not make the LLM responsible for everything.

The LLM is the reasoning component.

The backend remains the authority.

```text
User
 ↓
Sovereign Brain
 ↓
Context Engine
 ↓
Relevant Information
 ↓
LLM
 ↓
Decision
 ↓
Permission System
 ↓
Tools
 ↓
Observe Results
 ↓
Brain
 ↓
LLM
 ↓
Final Response
```

The architecture should therefore preserve a strict separation between:

```text
REASONING
    ↓
CONTEXT
    ↓
AUTHORITY
    ↓
EXECUTION
```

This allows Sovereign to begin as a fast local AI assistant and progressively evolve into a powerful autonomous agent without requiring a fundamental architectural rewrite.

---

# Final Golden Rule

> **Store everything as history.**
>
> **Remember selectively.**
>
> **Retrieve intelligently.**
>
> **Manage context deliberately.**
>
> **Keep structured data as the source of truth.**
>
> **Use vectors for semantic discovery, not as a replacement for structured data.**
>
> **Authorize every capability.**
>
> **Keep simple requests simple.**
>
> **Scale autonomy only when the task requires it.**

## Target Architecture

```text
                    ┌──────────────────┐
                    │     Browser      │
                    └────────┬─────────┘
                             │
                             ▼
                  ┌──────────────────────┐
                  │   Next.js Monolith   │
                  │        + BFF         │
                  │                      │
                  │ UI / Auth / Prisma   │
                  │ Sessions / API / SSE │
                  └──────────┬───────────┘
                             │
                         HTTP / SSE
                             │
                             ▼
                  ┌──────────────────────┐
                  │   Sovereign Brain    │
                  │       FastAPI        │
                  │                      │
                  │ Context Engine       │
                  │ Memory               │
                  │ RAG                  │
                  │ Tools                │
                  │ Permissions          │
                  │ Planner              │
                  └──────────┬───────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
               PostgreSQL          Ollama
                + pgvector          11434
                  5434
```

**This is the recommended long-term architecture for Project Sovereign.**
