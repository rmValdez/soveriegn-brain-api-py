# Architecture Decision: FastAPI Owns the Brain

## The conflict

Three sources describe Project Sovereign's architecture, and they don't agree:

1. **`a.md`** (original scaffold spec, this repo) — FastAPI owns Brain, Memory,
   Knowledge, Tools. Next.js is mentioned only as "later."
2. **`docs/WORKFLOW_AND_ROADMAP.md`** (both repos, identical) — explicit and
   detailed: *"Next.js is the application monolith. FastAPI is the
   intelligence engine."* FastAPI owns Context Engine, Memory, RAG, Tools,
   Permissions, Planner, agent loops. Next.js owns UI, auth, Prisma, BFF,
   SSE proxying.
3. **`docs/IMPLEMENTATION_PLAN.md`** (both repos, identical) — self-contradictory.
   Its header/diagram claims Next.js owns "Cognitive orchestration, Memory,
   RAG, Tools, Permissions/Confirmations, Planner" and Python is reduced to
   an "LLM abstraction... Model/inference communication" gateway. But the
   very next section in the *same file* ("Core Architectural Decision")
   says the opposite: "Python/FastAPI remains responsible for... Sovereign
   focuses on providing the cognitive behavior, orchestration, memory,
   tools, context, planning." The header was apparently edited (or drafted)
   without updating the body, or vice versa.

Meanwhile, the actual code in `src/app/modules/{brain,memory,knowledge,tools}/`
implements the full cognitive stack in Python — matching (1) and (2), not the
header of (3).

## Decision

**FastAPI is the intelligence engine. Next.js is the application shell.**

This is the position held by the original spec, the more detailed roadmap
doc, and 100% of the code written so far. Concretely:

| Concern | Owner |
|---|---|
| UI, routing, auth, Prisma, user preferences | Next.js |
| SSE proxy / BFF | Next.js |
| Brain orchestration, decisions | FastAPI |
| Context Engine (summarization, token budgeting) | FastAPI |
| Long-term memory (extraction + hybrid retrieval) | FastAPI |
| Knowledge / RAG (ingestion, chunking, pgvector search) | FastAPI |
| Tool registry + permission guardrails | FastAPI |
| Planner / multi-step execution | FastAPI |
| LLM/Ollama adapter, streaming, embeddings | FastAPI (`infrastructure/ollama/`) |

Next.js never talks to Ollama or the database's memory/knowledge/tool tables
directly — it always goes through the FastAPI Brain API.

## Why not the other way around

Moving Memory/RAG/Tools/Planner into Next.js (as `IMPLEMENTATION_PLAN.md`'s
header suggested) would mean:
- Rewriting ~6 already-implemented, already-tested Python modules in
  TypeScript for no functional gain.
- Splitting pgvector/SQLAlchemy access across two languages/ORMs (Prisma +
  SQLAlchemy) against the same tables — the "Do Not Vectorize Everything /
  keep Postgres as source of truth" principle gets harder to hold, not
  easier, once two runtimes write to it.
- Contradicting the project's own "no third backend language/runtime" and
  "pragmatic technology allocation" rules stated in the same document.

There's no cited reason for the pivot in either doc — it reads like a
draft edit that never got reconciled with the surrounding text.

## Action items

1. Fix `docs/IMPLEMENTATION_PLAN.md`'s header/diagram in both repos to match
   its own body text and `WORKFLOW_AND_ROADMAP.md` (Next.js = shell, FastAPI
   = brain). Currently it will mislead anyone who reads only the top of the
   file.
2. Treat `security.py`, `logging.py`, and `knowledge/service.py` (currently
   empty) as real work to finish in **this** repo — not placeholders for
   logic that's moving to Next.js.
3. Next.js's job regarding tools/permissions is UI only: render confirmation
   cards and call the approval endpoint. It does not implement permission
   logic itself — `PermissionGuard` in `tools/permissions.py` stays the
   single source of truth.
