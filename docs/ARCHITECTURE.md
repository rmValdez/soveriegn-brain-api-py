# Project Sovereign — Native Autonomous Agent Architecture

## Core Decision

Project Sovereign does **NOT integrate OpenClaw as an external agent framework**.

We are intentionally building our own **self-hosted, modular autonomous AI system**, inspired by the capabilities and agent-loop concepts demonstrated by systems such as OpenClaw.

OpenClaw is treated as a conceptual reference, not a runtime dependency.

The goal is to retain complete, uncompromised control over:
- The Brain & Cognitive Loop
- Context, Memory & Knowledge
- Tool Registry & Execution
- Planner & Multi-Step Reasoning
- Permission System & Safety Guardrails
- Model Selection & Ollama Runtime
- Local Data & Infrastructure

---

## 1. Core Architecture

```text
User
 │
 ▼
Next.js / React (Port 3008)
 │
 │ HTTP / SSE
 ▼
FastAPI Gateway (Port 3009)
 │
 ▼
Sovereign Brain
 │
 ├── Context
 │    ├── Conversation (Sessions & History)
 │    ├── Memory (Long-term Facts & Preferences)
 │    └── Knowledge (pgvector RAG)
 │
 ├── Decision Engine (Intent routing)
 │
 ├── Planner (Multi-step task plans)
 │
 ├── Tool Registry
 │    ├── Web
 │    ├── Calculator
 │    ├── Files
 │    ├── OS (Permission-gated)
 │    └── Future Extensions
 │
 └── LLM Runtime
      │
      ▼
    Ollama (Exclusive AI Engine: Port 11434)
```

**Ollama remains the ONLY AI/LLM runtime.** No OpenAI, Anthropic, Gemini, OpenRouter, or other external cloud providers.

---

## 2. The Brain Is the Core Orchestrator

The Brain is the central orchestrator:

```text
User
 ↓
Brain
 ↓
Understand request
 ↓
Determine what is needed
 ↓
Choose action
 ↓
Execute action
 ↓
Observe result
 ↓
Reason again
 ↓
Continue or finish
```

The Brain decides whether a request requires:
- Direct LLM response
- Memory retrieval
- Knowledge retrieval
- Tool execution
- Multi-step planning
- Final response generation

---

## 3. Simple Requests Must Stay Simple

The Brain must **NOT** invoke the entire agent system for every request.

- **Simple Request**:
  ```text
  "What is Python?" ➔ Brain ➔ Ollama ➔ Answer
  ```
  *(No planner. No web search. No filesystem. No unnecessary memory overhead.)*

- **Complex Request**:
  ```text
  "Review my project and tell me what I should improve."
  ➔ Brain ➔ Determine required context ➔ File Tool ➔ Observe results ➔ Ollama reasoning ➔ Final answer
  ```

The system uses the minimum capabilities necessary to complete the task accurately and fast.

---

## 4. Native Agent Loop

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
     Answer  Retrieve  Tool
              Context   Call
                         │
                         ▼
                      Observe
                         │
                         ▼
                       Brain
                         │
                         ▼
                  Continue / Finish
```

---

## 5. Planner as a Capability

The Planner does **NOT** hijack every request. It activates only when the Brain determines that a task requires multi-step decomposition.

The Planner is a **capability of the Brain**, not the Brain itself.

---

## 6. Memory vs. Knowledge

- **Conversation Context**: Short-term history of the active thread (PostgreSQL `sessions` & `messages`).
- **Long-Term Memory**: Structured facts, preferences, goals, and user context. Intentionally extracted and curated—never blindly saving every message as permanent memory.
- **Knowledge (RAG)**: Document extraction, chunking, Ollama embeddings, and semantic similarity search via `pgvector`.

---

## 7. Tool Registry & Strict Security

All tools reside in a centralized, decoupled registry:
```text
modules/tools/
├── registry.py
├── calculator.py
├── web.py
├── files.py
└── schemas.py
```

### ⚠️ Tool Security Rules
The LLM must **NEVER** receive unrestricted operating-system access.

```text
Ollama ➔ Brain ➔ Permission / Safety Layer ➔ Tool Execution
```

- Read-only operations are safe.
- Destructive or external actions (`delete`, `modify`, `send`, `deploy`, `git push`, `database mutation`) require explicit confirmation.
- The permission system is enforced strictly by Python code, **never** trusted to the model prompt.

---

## 8. Abstraction & On-Demand AI Lifecycle

```text
Brain ➔ LLMProvider (Abstract) ➔ OllamaAdapter (Concrete) ➔ Ollama
```

- **On-Demand Loading**: Models are loaded on request and allowed to unload after the configured `OLLAMA_KEEP_ALIVE` period (default `5m`) to conserve GPU resources.
- **Model Independence**: Configuration drives model selection (`OLLAMA_GENERAL_MODEL`, `OLLAMA_CODING_MODEL`, `OLLAMA_EMBEDDING_MODEL`) rather than hard-coding model names.

---

## 9. Incremental Development Roadmap

| Phase | Milestone | Status |
| :--- | :--- | :--- |
| **Phase 1** | FastAPI + Brain + `LLMProvider` + `OllamaAdapter` | ✅ Implemented |
| **Phase 2** | Sessions & Messages persistence (PostgreSQL) | ✅ Implemented |
| **Phase 3** | Connect Next.js frontend (Port 3008) via SSE | ✅ Implemented |
| **Phase 4** | Long-Term Memory curation & extraction | 🔄 Ready |
| **Phase 5** | Tool Registry & execution loop | 🔄 Ready |
| **Phase 6** | Knowledge ingestion & `pgvector` RAG | 🔄 Ready |
| **Phase 7** | Planner & dynamic multi-step execution | 🔄 Ready |
| **Phase 8** | Permission & Safety confirmation layer | 🔄 Ready |
| **Phase 9** | Production hardening & deployment | 🔄 Ready |
