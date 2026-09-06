# Skills System — Evaluation & Reconciled Plan

> Status: **draft, paused for next session.** Nothing in this document has
> been implemented. It exists so tomorrow's session starts from an honest
> baseline instead of re-litigating scope from scratch.

---

## 1. What was proposed vs. what already exists

A detailed "Skills System" proposal was pasted in, describing a generic
Skill/Tool framework: a `SkillRegistry`, typed skill definitions, a
`sovereign/skills/{core,information,system,development,...}` folder tree,
~29 sections covering everything from a calculator to browser automation,
email sending, and vision/OCR, organized into 10 new phases (Phase 0–10).

Before adopting any of it, here's what's actually already built and
running, verified against the code just now:

| Proposed | Reality |
|---|---|
| `SkillRegistry` (register/unregister/get/list/search/enable/disable) | Already exists: `tools/registry.py`'s `ToolRegistry` (register, get, get_all_definitions, execute, to_ollama_format). Narrower API (no unregister/enable/disable/search) but the same concept, already wired into the Brain. |
| `SkillResult` standard shape (`success, skill, data, error, metadata, duration_ms`) | Already exists: `tools/schemas.py`'s `ToolResult` (`success, tool_name, permission_level, data, error, status, duration_ms`). Different field names, same idea. |
| Permission system with risk levels | Already exists: `PermissionGuard` + `PermissionLevel` enum (`READ_ONLY`, `LOW_RISK`, `CONFIRMATION_REQUIRED`) — 3 levels, not the proposed 4 (`LOW/MEDIUM/HIGH/CRITICAL`). Already enforced, tested, and — as of this session — the path-traversal/`.env` guardrails were just hardened. |
| Confirmation workflow for dangerous skills | Already exists and is the most mature part of the whole system: pending-confirmation DB records, approve/reject endpoints, audit trail, real user attribution. Built and verified end-to-end this session. |
| `calculator` skill | Already exists: `tools/calculator.py`, real (not a scaffold). |
| `web_search` skill | **Exists but is fake** — `tools/web.py`'s handler literally returns `f"[Scaffold] Search results for: '{query}'. Mock data: 1. Example Result"`. This is the one "already have it" item that actually needs building from scratch. |
| `file_read`, `file_write`, `directory_list` | Exist (`tools/files.py`). `file_edit`, `file_delete`, `file_move`, `file_copy`, `file_search`, `directory_create` do not. |
| `git_status`, `git_log` (read-only) | Exist (`tools/git_tool.py`), already read-only-only as the proposal itself recommends starting with. `git_diff`, `git_branch`, `git_commit`, etc. don't exist. |
| `current_time`, `weather`, `terminal_execute`, coding-agent skills, database skills, model routing, planner, memory-as-skills, productivity, communication, browser, vision | None of these exist. |
| Knowledge/RAG skills | Overlaps entirely with **Phase 8** in `IMPLEMENTATION_PLAN.md` (already tracked: ingestion/retrieval scaffolding exists, `knowledge/service.py` aggregator is empty, no upload pipeline). |
| Planner (`task_decomposer`, `task_executor`, `task_verifier`) | Overlaps entirely with **Phase 9** (already tracked: `brain/planner.py` is a keyword-matcher today, not real planning). |
| Model routing | Overlaps entirely with **Phase 10** (already tracked in `KNOWN_ISSUES.md` #8: `OLLAMA_CODING_MODEL` is configured but nothing dispatches to it). |

**Bottom line:** roughly a third of "Phase 0" is already done. The genuinely
new, valuable, low-risk items are small (`current_time`, real `web_search`,
a handful of file operations). Most of the document's *volume* is in
categories (browser automation, email sending, terminal execution, finance,
IoT, vision) that are large, security-sensitive, and not something to
commit to in one sweep.

---

## 2. Two things to fix before writing any code

**a. This must not become a second roadmap.** The proposal's "Phase 0–10"
is a brand-new numbering scheme, separate from `IMPLEMENTATION_PLAN.md`'s
existing Phase 1–10. Adopting it as-is would recreate, a fourth time, the
exact problem this project already fixed three times this session:
multiple trackers drifting out of sync. Whatever gets built here extends
the *existing* Phase 6/7 (tools — done), Phase 8 (knowledge — in progress),
Phase 9 (planner — planned), and Phase 10 (production hardening/model
routing — planned). It does not get its own Phase 0–10.

**b. The folder structure doesn't match reality.** The proposal's
`sovereign/cognitive/`, `sovereign/skills/{category}/`, `sovereign/memory/`
tree doesn't correspond to either repo's actual layout. Per
`ARCHITECTURE_DECISION.md`, all of this lives in
`sovereign-brain-api-py/src/app/modules/tools/` (skills) and
`src/app/modules/brain/` (planner/orchestration) — not a new top-level
`sovereign/` tree, and not split into Next.js at all. If categorization is
wanted, it should be subpackages under the *existing* `modules/tools/`
(e.g. `modules/tools/filesystem/`, `modules/tools/web/`), not a parallel
tree.

**c. "Skill" vs "Tool" naming.** The proposal renames everything to
"Skill." The codebase, tests, DB table (`tool_executions`), and API routes
(`/api/v1/tools/*`) all say "Tool" today. Renaming is pure churn with no
functional benefit — recommend keeping "Tool" and treating "Skill" as the
proposal's own vocabulary, not something to adopt literally. Open for
discussion tomorrow if there's a reason to prefer "Skill" I'm missing.

---

## 3. What's actually worth prioritizing (reconciled, realistic)

Small, real, low-risk, no new open questions:

1. **`current_time`** — trivial, no external dependency, immediately useful, and directly prevents the model from guessing the current time/date (a real, observed failure mode of LLMs).
2. **Real `web_search`** — replace the mock in `tools/web.py` with an actual provider call. *Needs a decision: which provider/API (tomorrow's discussion).*
3. **Fill out `tools/files.py`**: `file_edit`, `file_delete`, `file_move`, `file_copy`, `file_search`, `directory_create` — same permission model already in place (`READ_ONLY` for search, `CONFIRMATION_REQUIRED` for delete/move/edit), same guardrails just hardened this session.
4. **4-level risk classification** (`LOW/MEDIUM/HIGH/CRITICAL` instead of the current 3) — worth evaluating once there are tools that actually need the extra granularity (e.g. `file_delete` vs `database_delete` probably shouldn't be the same risk tier). Not worth doing in the abstract before there's a concrete tool that needs it.

Needs an explicit decision before building, not a default yes:

5. **`weather`** — genuinely useful, but requires signing up for and storing a third-party API key/credential. Worth it, but a real external dependency to take on deliberately, not silently.
6. **`terminal_execute`** — the proposal itself calls this "HIGH RISK" and lists a long list of required guardrails (workspace restriction, timeout, output limits, process limits, audit logging) before it's safe. Given `files.py` had a real, unguarded gap until this session's fix, I'd want the sandboxing model actually proven out on file tools first before adding arbitrary command execution. Recommend treating this as its own dedicated planning/implementation pass, not part of a "basic skills" batch.
7. **Coding-agent skills** (`code_search`, `code_edit`, `run_tests`, etc.) and **git write skills** (`git_commit`, `git_branch`, ...) — real value, but this is effectively teaching Sovereign to modify its own two codebases. Wants its own scoping conversation about workspace boundaries (which repo(s) can it touch?) before any code.

Explicitly not now, revisit only if a real need shows up:

8. Database write skills, email/communication, browser automation, vision/OCR, productivity (calendar/reminders), finance, IoT. None of these have a concrete driving use case yet for a single-operator personal assistant; building them speculatively repeats the exact mistake already caught and reverted earlier this session (adding Redis/RabbitMQ before there was a concrete job for them).

---

## 4. Open decisions for next session

- Web search provider/API (and does it need a key)?
- Weather provider/API + where the API key gets stored (env var, per the
  proposal's own correct instinct — never in a prompt).
- Whether to expand `PermissionLevel` to 4 tiers now or wait for a tool
  that actually needs the distinction.
- Whether `terminal_execute` is wanted at all for this project, and if so,
  its own dedicated security design pass (workspace root, timeout, output
  caps, process limits) before any implementation.
- Workspace/repo boundaries for coding-agent and git-write skills, if
  pursued.
- Whether "Skill" terminology should actually replace "Tool" anywhere, or
  stay as-is.

None of this has been implemented. This file is the starting point for
picking the conversation back up.
