# Scaffold Personal AI Brain (From Scratch)

This document contains the complete specification for the **Personal AI Brain** project in the `soveriegn-brain-api-py` repository.

The project will be completely separate from the previous AI project.
The goal is to build a **general-purpose Personal AI Brain**, not simply a chatbot or coding assistant.

---

# 1. Core Architecture

The system will follow this architecture:

```text
User
  ↓
FastAPI
  ↓
Brain / Orchestrator
  ↓
┌─────────────────────────────────┐
│                                 │
│ Memory      Knowledge      Tools│
│                                 │
└─────────────────────────────────┘
  ↓
Ollama
  ↓
Local AI Model
```

The Brain is responsible for deciding what the user request requires.
Ollama is the **ONLY AI/LLM provider**.
No OpenAI API, Anthropic API, Gemini API, or other LLM provider will be added.

---

# 2. Project Initialization

Create:
* `pyproject.toml`
* `uv.lock`
* `.env.example`
* `.gitignore`
* `README.md`

Use:
* Python 3.13+
* `uv`
* `hatchling`

Recommended Python constraint:
```toml
requires-python = ">=3.13,<3.15"
```

## Core dependencies

```toml
dependencies = [
    "fastapi",
    "uvicorn[standard]",
    "sqlalchemy>=2.0",
    "psycopg[binary]",
    "pydantic>=2.13",
    "pydantic-settings",
    "alembic",
    "ollama",
]
```

Do not add LangChain or LlamaIndex initially.
The Brain orchestration should be implemented directly in Python so the architecture remains understandable and controllable.

---

# 3. Directory Structure

Create the following structure:

```text
soveriegn-brain-api-py/
│
├── src/
│   └── app/
│       │
│       ├── main.py
│       │
│       ├── api/
│       │   └── router.py
│       │
│       ├── core/
│       │   ├── config.py
│       │   ├── database.py
│       │   ├── logging.py
│       │   ├── exceptions.py
│       │   └── security.py
│       │
│       ├── modules/
│       │   │
│       │   ├── brain/
│       │   │   ├── orchestrator.py
│       │   │   ├── planner.py
│       │   │   ├── context.py
│       │   │   ├── decisions.py
│       │   │   └── schemas.py
│       │   │
│       │   ├── chat/
│       │   │   ├── router.py
│       │   │   ├── service.py
│       │   │   └── schemas.py
│       │   │
│       │   ├── memory/
│       │   │   ├── router.py
│       │   │   ├── service.py
│       │   │   ├── repository.py
│       │   │   ├── models.py
│       │   │   └── schemas.py
│       │   │
│       │   ├── knowledge/
│       │   │   ├── router.py
│       │   │   ├── ingestion.py
│       │   │   ├── retrieval.py
│       │   │   ├── service.py
│       │   │   └── schemas.py
│       │   │
│       │   ├── tools/
│       │   │   ├── registry.py
│       │   │   ├── calculator.py
│       │   │   ├── web.py
│       │   │   ├── files.py
│       │   │   └── schemas.py
│       │   │
│       │   └── sessions/
│       │       ├── models.py
│       │       ├── repository.py
│       │       └── service.py
│       │
│       └── infrastructure/
│           └── ollama/
│               ├── client.py
│               ├── chat.py
│               ├── embeddings.py
│               ├── models.py
│               └── exceptions.py
│
├── tests/
│
├── alembic/
│
├── pyproject.toml
├── uv.lock
├── .env.example
├── .gitignore
└── README.md
```

---

# 4. Important Architectural Rule

The application must NOT call Ollama directly from random modules.

Use this flow:
```text
Brain
  ↓
LLM Interface
  ↓
Ollama Adapter
  ↓
Ollama
```

The Ollama implementation belongs inside:
```text
src/app/infrastructure/ollama/
```

This keeps the Brain independent from the Ollama SDK implementation.
Even though Ollama is the only provider, this separation is important for maintainability.

---

# 5. Ollama Configuration

Create configuration through environment variables:

```env
APP_NAME=Sovereign Brain
APP_ENV=development

DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/sovereign_brain

OLLAMA_BASE_URL=http://localhost:11434

OLLAMA_GENERAL_MODEL=qwen3
OLLAMA_CODING_MODEL=qwen3-coder
OLLAMA_EMBEDDING_MODEL=embeddinggemma

OLLAMA_KEEP_ALIVE=5m
```

Do not hard-code model names throughout the application.
Create a centralized model configuration/registry.

---

# 6. Model Strategy

Initially use only a small number of Ollama models.

```text
General AI
    ↓
Qwen3

Coding
    ↓
Qwen3-Coder

Embeddings
    ↓
Ollama embedding model
```

Do not install many models immediately.
Start with:
1. One general model
2. One embedding model

Add the coding model after the basic Brain is working.
The system should select models based on the task rather than keeping every model loaded continuously.

---

# 7. On-Demand AI

The Personal AI Brain should NOT continuously consume GPU resources.

Desired behavior:
```text
No request
    ↓
Ollama idle

User request
    ↓
Brain
    ↓
Load required model
    ↓
Generate response
    ↓
Return response
    ↓
Model becomes idle/unloads according to configuration
```

Use Ollama's model lifecycle / `keep_alive` configuration.
This is especially important because the development machine uses an RTX 3060 12GB.
Do not design the system around unnecessarily large models.

---

# 8. Phase 1 — Basic Brain

The first implementation should be intentionally simple.

Build:
```text
POST /api/v1/chat
```

Flow:
```text
User
 ↓
Chat API
 ↓
Brain Orchestrator
 ↓
Ollama
 ↓
Response
```

The Brain should initially be able to:
* receive a user message
* send it to Ollama
* receive the response
* return the response
* stream the response
* handle Ollama connection errors
* handle invalid requests
* record basic request metadata

Do NOT implement complex autonomous planning yet.

---

# 9. Streaming

Implement streaming from the beginning.
Preferred initial transport:
```text
SSE
```

Example:
```text
POST /api/v1/chat/stream
```

Flow:
```text
Client
 ↓
FastAPI
 ↓
Brain
 ↓
Ollama
 ↓
token
token
token
token
 ↓
Client
```

WebSockets can be added later if the system requires true bidirectional realtime communication.

---

# 10. Brain Decision System

The Brain should eventually use structured decisions rather than parsing arbitrary natural-language instructions.

Example:
```python
class BrainDecision(BaseModel):
    action: Literal[
        "answer",
        "tool",
        "memory_search",
        "knowledge_search",
        "plan",
    ]

    tool_name: str | None = None

    requires_confirmation: bool = False
```

The important principle is:
```text
Ollama suggests the action.
Python controls the execution.
```

The model must never directly execute privileged operations.

---

# 11. Phase 2 — Sessions

Add conversation sessions.

Initial database entities:
```text
sessions
messages
```

Example flow:
```text
User
 ↓
Session
 ↓
Conversation history
 ↓
Brain
 ↓
Ollama
```

The Brain should be able to understand previous messages in the current session.

---

# 12. Phase 3 — Long-Term Memory

Separate conversation history from long-term memory.

Short-term:
```text
Session
 ↓
Messages
```

Long-term:
```text
Memory
├── Preferences
├── Projects
├── Goals
├── Decisions
└── Important personal context
```

Do NOT automatically save every conversation message as permanent memory.
Memory should be selectively extracted and stored.

The Brain should be able to:
```text
Search memory
 ↓
Retrieve relevant memories
 ↓
Add them to context
 ↓
Ask Ollama
```

---

# 13. Phase 4 — Tools

Create a centralized tool registry:
```text
Tool Registry
├── calculator
├── datetime
├── web_search
├── web_fetch
├── file_search
├── file_read
└── memory_search
```

Later:
```text
calendar
email
Git
GitHub
database
weather
maps
automation
custom APIs
```

Tools should be modular.
The Brain decides when a tool is necessary.

---

# 14. Tool Security

Never give the LLM unrestricted operating-system access.
Use permission boundaries.

Safe tools:
```text
read
search
calculate
retrieve
```

Potentially dangerous tools:
```text
delete
modify
send
execute
push
deploy
database mutation
```

Dangerous actions must require explicit application-level confirmation.
The security decision must happen outside the model.

Example:
```text
Ollama:
"Send this email"

        ↓

Brain

        ↓

Permission Check

        ↓

User Confirmation

        ↓

Execute
```

---

# 15. Phase 5 — Knowledge / RAG

Add personal knowledge later.

Supported documents should include:
```text
PDF
Markdown
TXT
DOCX
Source code
Notes
Documentation
```

Pipeline:
```text
Document
 ↓
Text extraction
 ↓
Chunking
 ↓
Ollama Embeddings
 ↓
PostgreSQL + pgvector
```

Query:
```text
User question
 ↓
Embedding
 ↓
Vector search
 ↓
Relevant chunks
 ↓
Brain
 ↓
Ollama
 ↓
Answer
```

Use PostgreSQL + pgvector instead of introducing a separate vector database initially.
Do not make RAG part of Phase 1.

---

# 16. Phase 6 — Planning

Only introduce complex planning after the basic Brain works.

Planning flow:
```text
User request
 ↓
Brain
 ↓
Create plan
 ↓
Execute required tools
 ↓
Collect results
 ↓
Reason over results
 ↓
Ollama
 ↓
Final response
```

Simple questions should NOT trigger planning.

Example:
```text
"What is Python?"
```

should simply:
```text
Brain → Ollama → Answer
```

While:
```text
"Analyze these documents, compare them, find the important differences,
and create a summary."
```

may require:
```text
Plan → Retrieve → Analyze → Summarize
```

---

# 17. Do Not Build an Agent Swarm

Do NOT initially create:
```text
Research Agent
Coding Agent
Memory Agent
Planning Agent
Document Agent
Supervisor Agent
Manager Agent
```

Instead use:
```text
                    ┌── Memory
                    ├── Knowledge
User → Brain ───────┼── Tools
                    ├── Planning
                    └── Ollama
```

The Brain is the orchestrator.

Specialized behavior should initially be represented by:
* tools
* models
* prompts
* structured decisions
* modules

Only create independent agents when there is a real architectural reason.

---

# 18. Database

Use:
```text
PostgreSQL
    +
SQLAlchemy 2.x Async
    +
Psycopg 3
    +
Alembic
```

Initial entities:
```text
users
sessions
messages
memories
```

Later:
```text
documents
document_chunks
tool_calls
tasks
model_runs
memory_events
plans
tool_permissions
```

Do not create every database table during the initial scaffold.
Create tables as each phase is implemented.

---

# 19. API Structure

Initial API:
```text
GET  /api/v1/health

POST /api/v1/chat
POST /api/v1/chat/stream

GET  /api/v1/sessions
GET  /api/v1/sessions/{id}
DELETE /api/v1/sessions/{id}
```

Later:
```text
GET    /api/v1/memories
POST   /api/v1/memories
DELETE /api/v1/memories/{id}

POST   /api/v1/knowledge
GET    /api/v1/knowledge

GET    /api/v1/tools
```

Keep the API modular and versioned.

---

# 20. Observability

Track:
```text
request_id
session_id
model
request duration
response duration
token usage when available
tool calls
tool latency
memory retrieval
knowledge retrieval
errors
```

Avoid logging sensitive personal content unnecessarily.

---

# 21. Security

Before exposing the Brain to the internet, implement:
```text
Authentication
Authorization
HTTPS
Rate limiting
Request validation
File upload limits
Tool permissions
Confirmation system
Audit logging
```

Most importantly:
```text
Internet
   ↓
Authenticated API
   ↓
Brain
   ↓
Ollama
```

NEVER:
```text
Internet
   ↓
Ollama :11434
```

Ollama should remain private.

---

# 22. Testing

Create tests from the beginning.

Initial tests:
```text
tests/
├── test_health.py
├── test_chat.py
├── test_brain.py
└── test_ollama.py
```

Later:
```text
test_memory.py
test_tools.py
test_knowledge.py
test_planner.py
test_permissions.py
```

The Brain logic should be testable without requiring every test to invoke a real model.

---

# 23. Development Phases

## Phase 1 — Brain + Ollama
```text
FastAPI
+
Brain
+
Ollama
+
Chat
+
Streaming
```
Goal:
```text
User → Brain → Ollama → Response
```

## Phase 2 — Sessions
```text
PostgreSQL
+
Sessions
+
Messages
+
Conversation context
```

## Phase 3 — Memory
```text
Long-term memory
+
Memory retrieval
+
Memory extraction
```

## Phase 4 — Tools
```text
Tool registry
+
Calculator
+
Web
+
Files
+
Memory search
```

## Phase 5 — Knowledge
```text
Document ingestion
+
Ollama embeddings
+
pgvector
+
RAG
```

## Phase 6 — Planning
```text
Brain
+
Plans
+
Multi-step execution
+
Tool orchestration
```

## Phase 7 — Personalization
Add:
```text
Preferences
Projects
Goals
Personal knowledge
Behavior customization
```

The Brain should gradually become personalized to the user rather than behaving like a generic chatbot.

## Phase 8 — Online Deployment
Eventually:
```text
React / Next.js
        ↓
Authenticated API
        ↓
Sovereign Brain
        ↓
PostgreSQL
        ↓
Ollama
```
Ollama remains private behind the backend.

---

# 24. Initial Technology Decisions

```text
Language: Python 3.13+
Backend: FastAPI
ORM: SQLAlchemy 2.x Async
Database: PostgreSQL
Database Driver: Psycopg 3
Migrations: Alembic
Validation: Pydantic v2
Configuration: pydantic-settings
Package Manager: uv
Build System: Hatchling
AI Runtime: Ollama ONLY
General Model: Qwen3
Coding Model: Qwen3-Coder
Embedding Model: Ollama embedding model
Vector Search: pgvector
Frontend: React / Next.js later
Architecture: Modular / Domain-Oriented
AI Architecture: Brain + Memory + Knowledge + Tools
Deployment: Local first → Secure online later
```

---

# 25. Scaffold Verification

After generating the project:
```bash
cd soveriegn-brain-api-py
```
Verify the structure:
```bash
tree src
```
Then:
```bash
uv sync
```
Verify Python:
```bash
python --version
```
Verify Ollama:
```bash
ollama list
```
Verify the API:
```bash
uv run uvicorn app.main:app --reload
```
Then verify:
```text
GET /api/v1/health
```

---

# 26. Important Rule for the Initial Scaffold

The scaffold should create the architecture and boilerplate, but it should NOT pretend that every feature is already implemented.

Initially:
```text
Brain
    ↓
Ollama
    ↓
Chat
```

Everything else can be introduced incrementally.
Avoid creating fake implementations, placeholder agents, unnecessary abstractions, or unused dependencies.
Every module should eventually have a real responsibility.

---

# Final Goal

The goal of `soveriegn-brain-api-py` is not to create another chatbot.
The goal is to build a **Sovereign Personal AI Brain** that can eventually:

```text
Understand the user
       ↓
Remember important information
       ↓
Understand personal knowledge
       ↓
Use tools
       ↓
Research
       ↓
Plan complex tasks
       ↓
Work with documents
       ↓
Assist with coding
       ↓
Learn the user's preferences
       ↓
Execute approved actions
       ↓
Respond intelligently
```

with:
```text
Python
+
FastAPI
+
PostgreSQL
+
pgvector
+
Tools
+
Memory
+
Knowledge
+
Brain Orchestration
+
Ollama
```

**Ollama is the only AI provider.**

The application itself owns the intelligence architecture: the Brain, memory, tools, permissions, context, planning, and knowledge system.

The implementation should therefore follow:
```text
BUILD THE BRAIN FIRST.
ADD CAPABILITIES ONE AT A TIME.
KEEP OLLAMA AS THE AI RUNTIME.
KEEP THE SYSTEM ON-DEMAND.
KEEP SECURITY OUTSIDE THE MODEL.
```
