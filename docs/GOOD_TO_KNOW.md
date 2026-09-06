# 💡 Good to Know: Junior Developer Guide

Welcome to the **Sovereign Personal AI Brain** codebase! This guide compiles essential concepts, patterns, design decisions, and common pitfalls to help you ship code quickly and confidently.

---

## 1. Core Philosophies & Rules of Engagement

1. **Strict Local Sovereignty**: 
   - Never install or import third-party cloud AI packages (like `openai`, `anthropic`, or `google-generativeai`). 
   - All AI inference and embedding generation MUST route through our local **Ollama** infrastructure (`src/app/infrastructure/ollama`).
2. **Async Everywhere**:
   - We use Python's `asyncio` ecosystem across the entire stack.
   - All FastAPI route handlers, database calls, and HTTP requests must use `async`/`await`.
   - Never use blocking functions (e.g., standard `time.sleep()`, synchronous `requests.get()`, or synchronous file I/O in the hot path). Use `asyncio.sleep()`, `httpx.AsyncClient()`, or `aiofiles`.
3. **Pydantic V2 Conventions**:
   - We use Pydantic V2. 
   - When converting SQLAlchemy models to Pydantic schemas, use `from_attributes = True` inside `model_config = ConfigDict(from_attributes=True)` or `class Config: from_attributes = True`. (Do **not** use the deprecated `orm_mode = True`).
   - Use `MySchema.model_validate(db_obj)` instead of `MySchema.from_orm(db_obj)`.

---

## 2. Top 5 Gotchas & How to Avoid Them

### 🚨 Gotcha 1: Async SQLAlchemy & `MissingGreenlet` Error
* **The Problem**: In synchronous SQLAlchemy, accessing a relationship (like `session.messages`) will automatically trigger a database query behind the scenes. In **Async SQLAlchemy**, doing this triggers:
  ```text
  MissingGreenlet: greenlet_spawn has not been called; can't call await_only() here.
  ```
* **The Fix**:
  1. On your model relationship definition, always specify `lazy="selectin"`:
     ```python
     messages = relationship("Message", back_populates="session", lazy="selectin")
     ```
  2. When querying in repositories, explicitly load relationships using `selectinload`:
     ```python
     from sqlalchemy.orm import selectinload

     stmt = select(Session).where(Session.id == session_id).options(selectinload(Session.messages))
     ```

---

### 🚨 Gotcha 2: pgvector & Alembic Migrations
* **The Problem**: Alembic's `--autogenerate` detects the `Vector` column, but it often forgets two critical things:
  1. It doesn't import the `pgvector` library inside the migration script.
  2. It doesn't enable the Postgres `vector` extension before trying to create tables with vector columns.
* **The Fix**: Whenever a new migration with vector columns is generated in `alembic/versions/`:
  - Ensure `import pgvector.sqlalchemy` is present at the top of the file.
  - Add `op.execute("CREATE EXTENSION IF NOT EXISTS vector;")` at the very beginning of the `upgrade()` function:
    ```python
    def upgrade() -> None:
        op.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        # ... op.create_table(...)
    ```

---

### 🚨 Gotcha 3: Docker Networking vs. `localhost` (Ollama)
* **The Problem**: When running the API inside Docker, `http://localhost:11434` refers to **the inside of the Docker container**, not your computer.
* **The Fix**:
  - We use `http://host.docker.internal:11434` to reach the Ollama instance running on your host machine.
  - In `docker-compose.yml`, this is already configured via the environment variable `OLLAMA_BASE_URL=http://host.docker.internal:11434`.

---

### 🚨 Gotcha 4: Database Port Mapping (`5434` vs `5432`)
* **The Problem**: Many developers already have PostgreSQL running locally on port `5432` or `5433` for other projects.
* **The Fix**:
  - Our `docker-compose.yml` maps host port `5434` to container port `5432`:
    ```yaml
    ports:
      - "5434:5432"
    ```
  - **Inside Docker** (API container): Connect using `db:5432`.
  - **Outside Docker** (DBeaver, TablePlus, or psql on your host machine): Connect using `localhost:5434`.

---

### 🚨 Gotcha 5: CORS with Next.js Frontend
* **Not the load-bearing mechanism it used to be**: the browser no longer calls this API directly — `soveriegn-brain-app` proxies everything server-side through its BFF (`src/app/api/**`), which isn't subject to CORS at all (server-to-server). `CORSMiddleware` in `src/app/main.py` still exists and matters if you hit this API directly from a browser (Swagger UI at `/docs`, manual testing, a future non-Next.js client), but it is not what connects the real app to the browser anymore.
* If you add a new direct-from-browser caller, add its origin to `allow_origins` in `main.py` — but first ask whether it should go through the Next.js BFF instead, per `docs/ARCHITECTURE_DECISION.md`.

---

## 3. Step-by-Step Cookbooks

### 🛠️ Cookbook A: How to Add a New Tool
To give the AI Brain a new capability (e.g., getting weather, querying an internal database, running code):

1. Create a new tool file in `src/app/modules/tools/` (e.g., `weather.py`):
   ```python
   from pydantic import BaseModel, Field
   from .schemas import BaseTool, ToolResult

   class WeatherArgs(BaseModel):
       city: str = Field(..., description="The city name to check weather for")

   class WeatherTool(BaseTool):
       name: str = "get_weather"
       description: str = "Retrieves current weather information for a given city"
       args_schema: type[BaseModel] = WeatherArgs

       async def execute(self, city: str) -> ToolResult:
           try:
               # Your async logic here
               temp = 22.5
               return ToolResult(success=True, data=f"The weather in {city} is {temp}°C.")
           except Exception as e:
               return ToolResult(success=False, error=str(e))
   ```

2. Register the tool in `src/app/modules/tools/registry.py`:
   ```python
   from .weather import WeatherTool

   registry.register(WeatherTool())
   ```

3. That's it! The `PlannerService` and `ToolRegistry` will now discover and make this tool available.

---

### 🗄️ Cookbook B: How to Add a New Database Model
1. Define your SQLAlchemy model in `src/app/modules/<your_module>/models.py`:
   ```python
   from sqlalchemy import Column, String, DateTime
   from app.core.database import Base

   class CustomEntity(Base):
       __tablename__ = "custom_entities"
       id = Column(String, primary_key=True)
       name = Column(String, nullable=False)
   ```

2. Register your model in `alembic/env.py`:
   ```python
   from app.modules.<your_module> import models as custom_models
   ```

3. Generate and apply the migration via Docker:
   ```bash
   docker compose exec api uv run alembic revision --autogenerate -m "add_custom_entities"
   docker compose exec api uv run alembic upgrade head
   ```

---

### 🌐 Cookbook C: How to Add a New API Route
1. Define your router in `src/app/modules/<your_module>/router.py`:
   ```python
   from fastapi import APIRouter, Depends
   from sqlalchemy.ext.asyncio import AsyncSession
   from app.core.database import get_db

   router = APIRouter(prefix="/api/v1/items", tags=["Items"])

   @router.get("")
   async def list_items(db: AsyncSession = Depends(get_db)):
       return {"items": []}
   ```

2. Mount your router in `src/app/main.py`:
   ```python
   from app.modules.<your_module>.router import router as custom_router

   app.include_router(custom_router)
   ```

---

## 4. Helpful Daily Commands

| Task | Command |
| :--- | :--- |
| **Start everything (detached)** | `docker compose up -d` |
| **Rebuild after changing dependencies** | `docker compose up -d --build` |
| **Stream live API logs** | `docker compose logs -f api` |
| **Run unit tests inside container** | `docker compose exec api uv run pytest` |
| **Open a shell inside the API container** | `docker compose exec api bash` |
| **Check container health status** | `docker compose ps` |
| **Stop all containers** | `docker compose down` |

---

## 5. Directory Reference Quick-Map

```text
src/app/
├── core/             <-- App settings, database engine, Base class
├── infrastructure/   <-- Ollama client, external protocols
└── modules/
    ├── brain/        <-- AI Orchestration & Planning logic
    ├── chat/         <-- User chat endpoints & streaming
    ├── knowledge/    <-- Document chunking & pgvector RAG
    ├── memory/       <-- Long-term persistent user memories
    ├── sessions/     <-- Multi-turn session & message history
    └── tools/        <-- Action registry and concrete tools
```
