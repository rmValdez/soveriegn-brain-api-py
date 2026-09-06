# Project Sovereign — Native Autonomous Agent Architecture

## Core Decision

Project Sovereign does **NOT integrate OpenClaw as an external agent framework**.

We are intentionally building our own **self-hosted, modular autonomous AI system**, inspired by the capabilities and agent-loop concepts demonstrated by systems such as OpenClaw.

OpenClaw is treated as a conceptual reference, not a runtime dependency.

The goal is to retain complete control over:

* Brain & cognitive loop
* Context, memory & knowledge
* Tool registry & execution
* Planning & multi-step reasoning
* Permissions & safety guardrails
* Model selection & Ollama runtime
* Local data & infrastructure

---

# 1. Core Architecture

```text
User
 │
 ▼
Next.js / React
Port 3008
 │
 │ HTTP / SSE
 ▼
FastAPI Gateway
Port 3009
 │
 ▼
Sovereign Brain
 │
 ├── Context
 │    ├── Conversation
 │    ├── Memory
 │    └── Knowledge
 │
 ├── Decision Engine
 │
 ├── Planner
 │
 ├── Permission / Safety Layer
 │
 ├── Tool Registry
 │    ├── Web
 │    ├── Calculator
 │    ├── Files
 │    ├── OS
 │    └── Future Extensions
 │
 └── LLM Runtime
      │
      ▼
    Ollama
    Port 11434
```

Ollama remains the **ONLY AI/LLM runtime**.

No OpenAI, Anthropic, Gemini, OpenRouter, or other external LLM provider should be introduced.

---

# 2. The Brain Is the Core Orchestrator

The Brain is the central cognitive orchestrator.

Its fundamental loop is:

```text
User Request
     ↓
Understand
     ↓
Build Context
     ↓
Decide Next Action
     ↓
Execute / Generate
     ↓
Observe Result
     ↓
Evaluate
     ↓
Continue OR Finish
```

The Brain determines whether a request requires:

* direct LLM generation
* conversation context
* memory retrieval
* knowledge retrieval
* tool execution
* planning
* multiple actions
* additional reasoning
* final response generation

The Brain should remain the central authority for agent execution.

---

# 3. Simple Requests Must Stay Simple

The system must avoid unnecessary agent complexity.

Example:

```text
"What is Python?"

        ↓
      Brain
        ↓
      Ollama
        ↓
      Answer
```

No unnecessary:

* planner
* web search
* filesystem access
* memory retrieval
* multi-step execution

For complex tasks:

```text
"Review my project and tell me what I should improve."

        ↓
      Brain
        ↓
 Determine required context
        ↓
 File / Knowledge retrieval
        ↓
      Observe
        ↓
   Ollama reasoning
        ↓
      Final answer
```

The Brain should use the **minimum capabilities necessary** to complete a request accurately.

---

# 4. Native Agent Loop

The long-term execution model is:

```text
┌─────────────────────────────┐
│            USER             │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│            BRAIN            │
│                             │
│ Understand request          │
│ Build context               │
│ Decide next action          │
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
                      Permission
                         │
                         ▼
                      Execute
                         │
                         ▼
                       Observe
                         │
                         ▼
                        Brain
                         │
                  ┌──────┴──────┐
                  ▼             ▼
               Continue       Finish
```

This loop is the core autonomous behavior of Project Sovereign.

---

# 5. Planner Is a Brain Capability

The Planner must NOT control every request.

It activates only when the Brain determines that a task requires multi-step decomposition.

Example:

```text
Simple:
"Calculate 25 × 4"

Brain
 ↓
Calculator
 ↓
Answer
```

Complex:

```text
"Research three hosting providers,
compare them,
inspect my project's requirements,
and recommend one."

Brain
 ↓
Planner
 ↓
Create execution plan
 ↓
Tool execution
 ↓
Observe results
 ↓
Additional actions if required
 ↓
Ollama reasoning
 ↓
Final response
```

The Planner is therefore a **capability of the Brain**, not a replacement for the Brain.

---

# 6. Context, Memory & Knowledge

These must remain separate concepts.

### Conversation Context

Short-term context belonging to the active conversation.

```text
sessions
messages
conversation history
```

Stored in PostgreSQL.

### Long-Term Memory

Curated information that is intentionally retained.

Examples:

```text
preferences
important facts
projects
goals
decisions
recurring context
```

Do NOT blindly save every conversation message as permanent memory.

Memory extraction and retention should be intentional.

### Knowledge

External or user-provided information that can be retrieved.

```text
Documents
 ↓
Extraction
 ↓
Chunking
 ↓
Ollama Embeddings
 ↓
pgvector
 ↓
Semantic Retrieval
 ↓
Brain
 ↓
Ollama
```

Memory and Knowledge must not be treated as the same subsystem.

---

# 7. Tool Registry

All tools must be centralized and decoupled from the Brain.

Recommended structure:

```text
src/app/modules/tools/

├── registry.py
├── calculator.py
├── web.py
├── files.py
├── os.py
├── schemas.py
└── permissions.py
```

The Brain should interact with tools through the registry.

```text
Brain
 ↓
Tool Registry
 ↓
Permission / Safety Layer
 ↓
Selected Tool
 ↓
Execution
 ↓
Tool Result
 ↓
Brain
```

The Brain should not directly import arbitrary tool implementations throughout the application.

---

# 8. Security Is Part of the Execution Architecture

The LLM must **NEVER** receive unrestricted operating-system access.

Never implement:

```text
Ollama
 ↓
arbitrary shell command
```

Instead:

```text
Ollama
 ↓
Brain
 ↓
Tool Request
 ↓
Permission / Safety Layer
 ↓
Tool
 ↓
Execution
 ↓
Result
 ↓
Brain
```

The model may request an action.

The application decides whether that action is permitted.

The permission system must be enforced by Python/application code and must NOT depend on prompt instructions.

Potentially dangerous operations include:

```text
delete
modify
send
deploy
git push
database mutation
file destruction
system configuration changes
```

These require explicit authorization/confirmation according to the tool's permission policy.

---

# 9. Tool Permission Model

Every tool should declare its execution characteristics.

Conceptually:

```text
Tool
├── name
├── description
├── input schema
├── output schema
├── risk level
├── required permission
└── confirmation requirement
```

For example:

```text
calculator
→ read-only
→ no confirmation

file_read
→ read-only
→ no confirmation

file_write
→ mutation
→ confirmation

git_push
→ external mutation
→ confirmation

system_command
→ high risk
→ restricted
```

The permission layer must be deterministic and enforceable independently of the LLM.

---

# 10. LLM Abstraction

The Brain must not directly depend on Ollama implementation details.

Use:

```text
Brain
 ↓
LLMProvider
 ↓
OllamaAdapter
 ↓
Ollama
```

`LLMProvider` defines the interface.

`OllamaAdapter` implements the interface.

Ollama remains the only production provider.

The abstraction exists for:

* clean architecture
* testing
* isolation
* maintainability
* future flexibility

It does NOT imply that cloud providers should be added.

---

# 11. Model Selection

Do not hard-code a specific Qwen generation into the architecture.

Use configuration:

```env
OLLAMA_BASE_URL=http://localhost:11434

OLLAMA_GENERAL_MODEL=qwen3

OLLAMA_CODING_MODEL=qwen3-coder

OLLAMA_EMBEDDING_MODEL=embeddinggemma

OLLAMA_KEEP_ALIVE=5m
```

The Brain may eventually select a model based on task type.

For example:

```text
General question
→ General model

Coding task
→ Coding model

Semantic retrieval
→ Embedding model
```

The architecture depends on Ollama, not on one specific model version.

---

# 12. On-Demand AI Lifecycle

Models must NOT be unnecessarily preloaded during FastAPI startup.

The intended lifecycle is:

```text
Request
 ↓
Brain
 ↓
Ollama
 ↓
Load model when required
 ↓
Inference
 ↓
Response
 ↓
Model remains available according to keep-alive policy
 ↓
Unload when idle
```

This preserves GPU resources during periods of inactivity.

---

# 13. No Multi-Agent Swarm Initially

Do NOT immediately create:

```text
Research Agent
Coding Agent
Memory Agent
Planner Agent
Supervisor Agent
Manager Agent
```

Start with one Brain:

```text
Brain
├── Context
├── Memory
├── Knowledge
├── Tools
├── Planner
└── Ollama
```

Specialized agents should only be introduced if real workloads demonstrate that they are necessary.

---

# 14. No Heavy Agent Framework Initially

Do not introduce LangChain, LlamaIndex, or another large orchestration framework merely because Project Sovereign is an agent.

Initially implement orchestration directly in Python.

This provides:

* full control
* easier debugging
* easier security auditing
* less framework lock-in
* better understanding of the system
* simpler architecture

External libraries may be introduced later when they solve a concrete problem better than native implementation.

---

# 15. Frontend Responsibility

Next.js remains the interface layer.

```text
Next.js
├── Server Components
├── Client Components
├── Server Actions
├── SSR
└── SSE
```

The frontend must NOT contain Brain logic.

Do not implement the following inside Next.js:

```text
Planner
Memory engine
Tool execution
RAG orchestration
Agent loop
Permission enforcement
```

These belong to the FastAPI backend.

The frontend communicates with Sovereign through HTTP/SSE.

---

# 16. Database

Use PostgreSQL as the primary persistent datastore.

Initial:

```text
PostgreSQL
├── sessions
└── messages
```

Later:

```text
PostgreSQL
├── sessions
├── messages
├── memories
├── documents
├── document_chunks
├── tool_calls
├── plans
└── tasks
```

Use pgvector for semantic knowledge retrieval when Knowledge/RAG is implemented.

---

# 17. Observability

Because Sovereign will eventually perform autonomous actions, execution should be observable.

Record important events such as:

```text
request
brain decision
context retrieval
memory retrieval
knowledge retrieval
tool request
permission decision
tool execution
tool result
LLM invocation
final response
errors
```

This allows us to understand:

* why the Brain made a decision
* which tools were used
* what information was retrieved
* where execution failed
* how much work a task required

Do not expose sensitive internal information to the user interface unnecessarily.

---

# 18. Incremental Development Roadmap

> **See `IMPLEMENTATION_PLAN.md` for the current, authoritative phase-status
> table.** This doc’s phase numbering predates that tracker and had drifted
> out of sync with it (e.g. this table showed Memory/Tools/Knowledge/Planner
> all still "Ready" i.e. not started, while `IMPLEMENTATION_PLAN.md` showed
> most of them completed and tested). Rather than keep a third copy, this
> section defers to the one tracker.

### Important

The basic permission/safety boundary must exist **before any dangerous tool is exposed**. That boundary (`PermissionGuard`, tool confirmation workflow, audit trail) is implemented and tested — see Phase 6/7 in `IMPLEMENTATION_PLAN.md`. Remaining security work (API auth, rate limiting) is tracked there under Phase 10.

---

# 19. Recommended Implementation Order From Here

The safest next progression (see `IMPLEMENTATION_PLAN.md` for which of these
are already done vs. still open) is:

```text
Memory
 ↓
Tools + Permission Boundary
 ↓
Knowledge / RAG
 ↓
Planner + Agent Loop
 ↓
Advanced Security / Confirmations
 ↓
Production Hardening
```

This gives the Brain progressively more capabilities without introducing the full autonomous system all at once.

---

# 20. Target Architecture

```text
                         PROJECT SOVEREIGN
                                │
                 ┌──────────────┴──────────────┐
                 │                             │
          SOVEREIGN APP                SOVEREIGN BRAIN
          Next.js / React              Python / FastAPI
                 │                             │
                 │                        ┌────┴────┐
                 │                        │  BRAIN  │
                 │                        └────┬────┘
                 │                             │
                 │              ┌──────────────┼──────────────┐
                 │              │              │              │
                 │           Memory        Knowledge        Tools
                 │              │              │              │
                 │              └──────────────┼──────────────┘
                 │                             │
                 │                          Planner
                 │                             │
                 │                      Permission Layer
                 │                             │
                 │                             ▼
                 │                           Ollama
                 │
                 └──────────── HTTP / SSE ────────────────┘
```

---

# Final Architectural Principle

Project Sovereign is:

> **A self-hosted, modular autonomous AI system with its own Brain, cognitive loop, memory, knowledge retrieval, tools, planning, permissions, and execution system, powered exclusively by Ollama.**

OpenClaw is a conceptual reference only.

We are NOT building an OpenClaw wrapper.

We are building Sovereign's own agent architecture.

The fundamental loop is:

```text
User
 ↓
Brain
 ↓
Understand
 ↓
Context
 ↓
Decide
 ↓
Plan if necessary
 ↓
Request tool if necessary
 ↓
Permission check
 ↓
Execute
 ↓
Observe
 ↓
Reason
 ↓
Continue or Finish
```

The system should remain:

**modular**

**self-hosted**

**Ollama-only**

**on-demand**

**secure**

**observable**

**extensible**

and **controlled by application code rather than by the LLM itself.**
