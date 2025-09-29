from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.base import init_db
import asyncio
from app.api.routes import connections
from app.api.routes import dicts
from app.api.routes import ticket
from app.api.routes import servers
from app.api.routes import ssh

app = FastAPI(title="db_expert Backend", version="0.1.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=getattr(settings, "CORS_ORIGIN_REGEX", None),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(connections.router, prefix="/api/connections", tags=["connections"]) 
app.include_router(dicts.router)  # exposes /api/dicts/{dm}
app.include_router(ticket.router)  # exposes /api/ticket/* and /api/connections/{id}/* (tables/databases)
app.include_router(servers.router, prefix="/api/servers", tags=["servers"])  # servers CRUD & test
app.include_router(ssh.router)  # exposes /api/ssh/ws (WebSSH)


@app.on_event("startup")
async def on_startup():
    # 避免因数据库不可达导致应用启动阻塞：
    try:
        await asyncio.wait_for(init_db(), timeout=10)
    except Exception as e:
        # 记录错误并继续启动；在后台重试一次，以便数据库稍后可用时自动建表/预热
        try:
            print(f"[startup] init_db failed or timed out: {e}")
        except Exception:
            pass
        try:
            asyncio.create_task(init_db())
        except Exception:
            pass


@app.get("/health")
def health():
    return {"status": "ok"}
