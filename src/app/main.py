from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.modules.chat.router import router as chat_router
from app.modules.sessions.router import router as sessions_router
from app.modules.memory.router import router as memory_router
from app.modules.knowledge.router import router as knowledge_router

app = FastAPI(title=settings.app_name)

# Enable CORS for Next.js frontend (port 3008) and other clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3008",
        "http://127.0.0.1:3008",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "app_name": settings.app_name, "env": settings.app_env}

app.include_router(chat_router, prefix="/api/v1")
app.include_router(sessions_router, prefix="/api/v1")
app.include_router(memory_router)
app.include_router(knowledge_router)
