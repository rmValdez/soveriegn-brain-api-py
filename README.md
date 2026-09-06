# Sovereign Personal AI Brain API

A modular, self-hosted Personal AI Brain API backend built with **FastAPI**, **SQLAlchemy Async**, **PostgreSQL (pgvector)**, and **Ollama**.

---

## 🏗️ Project Architecture & Structure

The repository follows a clean, modular architecture separating concerns across infrastructure, core database/config, and domain feature modules:

```text
sovereign-brain-api-py/
├── alembic/                      # Database migrations
│   ├── versions/                 # Versioned migration scripts (with pgvector support)
│   └── env.py                    # Async migration runner & metadata discovery
├── scripts/
│   └── entrypoint.sh             # Docker entrypoint (auto-runs migrations & uvicorn)
├── src/
│   └── app/
│       ├── core/                 # App-wide configuration & base database setup
│       │   ├── config.py         # Pydantic Settings (.env loader)
│       │   └── database.py       # Async SQLAlchemy engine & session factory
│       ├── infrastructure/       # External clients & service integrations
│       │   └── ollama/           # Local LLM client (chat completions, streaming, embeddings)
│       ├── modules/              # Domain-specific modules
│       │   ├── brain/            # Cognitive orchestrator, decision parser & planning
│       │   ├── chat/             # Chat endpoints & streaming SSE responses
│       │   ├── knowledge/        # Document ingestion, pgvector chunking & RAG search
│       │   ├── memory/           # Long-term memory store (preferences, goals, facts)
│       │   ├── sessions/         # Chat threads, history persistence & auto-titling
│       │   └── tools/            # Tool registry & execution engine (calculator, web, files)
│       └── main.py               # FastAPI application setup, CORS middleware & router mounts
├── .env.example                  # Environment configuration template
├── docker-compose.yml            # Docker orchestration (FastAPI + PostgreSQL pgvector)
├── Dockerfile                    # Container definition (Python 3.13 + Astral uv)
├── pyproject.toml                # Dependencies and project metadata
└── uv.lock                       # Deterministic dependency lockfile
```

---

## ⚙️ Prerequisites

1. **Docker Desktop** installed and running.
2. **Ollama** installed on your host machine (listening on default `http://localhost:11434`).
   - Recommended models:
     ```bash
     ollama pull qwen3
     ollama pull embeddinggemma
     ```

---

## 🚀 How to Run

### Method 1: Docker (Recommended)

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rmValdez/sovereign-brain-api-py.git
   cd sovereign-brain-api-py
   ```

2. **Configure environment** (optional):
   ```bash
   cp .env.example .env
   ```

3. **Start the containers**:
   ```bash
   docker compose up -d --build
   ```

   - **FastAPI Backend**: [http://localhost:3009](http://localhost:3009)
   - **Interactive API Docs (Swagger UI)**: [http://localhost:3009/docs](http://localhost:3009/docs)
   - **PostgreSQL Database**: Port `5434` (mapped from `5432` to avoid host collisions)

> **Live Code Reloading**: The local `./src` directory is mounted into the container. Any code changes made locally will immediately trigger an automatic reload inside the container.

#### Useful Docker Commands:
```bash
# View live API logs
docker compose logs -f api

# Stop containers
docker compose down

# Run database migrations manually inside container
docker compose exec api uv run alembic upgrade head
```

---

### Method 2: Local Development (Without Docker)

1. **Install dependencies** using [uv](https://github.com/astral-sh/uv):
   ```bash
   uv sync
   ```

2. **Configure `.env`**:
   Ensure `DATABASE_URL` points to a running PostgreSQL instance with `pgvector` enabled:
   ```ini
   DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/sovereign_brain
   OLLAMA_BASE_URL=http://localhost:11434
   ```

3. **Run database migrations**:
   ```bash
   uv run alembic upgrade head
   ```

4. **Start the development server**:
   ```bash
   uv run uvicorn app.main:app --host 0.0.0.0 --port 3009 --reload
   ```

---

## 📡 API Overview

| Tag | Endpoint | Method | Description |
| :--- | :--- | :--- | :--- |
| **Health** | `/api/v1/health` | `GET` | Health check & environment status |
| **Chat** | `/api/v1/chat` | `POST` | Standard chat completion with orchestrator |
| **Chat** | `/api/v1/chat/stream` | `POST` | Server-Sent Events (SSE) streaming chat |
| **Sessions**| `/api/v1/sessions` | `GET` | List all chat sessions |
| **Sessions**| `/api/v1/sessions` | `POST` | Create a new chat session |
| **Sessions**| `/api/v1/sessions/{id}` | `GET` | Get session details & full message history |
| **Sessions**| `/api/v1/sessions/{id}` | `DELETE`| Delete a session and its messages |
| **Memory** | `/api/v1/memories` | `POST` | Store categorized memory (preference, goal, fact) |
| **Memory** | `/api/v1/memories/user/{user_id}` | `GET` | Get all stored memories for a user |
| **Knowledge**| `/api/v1/knowledge/ingest` | `POST` | Ingest document, chunk & compute embeddings |
| **Knowledge**| `/api/v1/knowledge/search` | `POST` | Query knowledge base via vector similarity search |

---

## 💻 Frontend (Next.js / Vite) Integration

The API comes with **CORS enabled** (`http://localhost:3000` allowed by default). You can connect a Next.js or React frontend directly to `http://localhost:3009`.
