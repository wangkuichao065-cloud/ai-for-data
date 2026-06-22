"""FastAPI 应用入口 — main.py"""
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# 将 backend 目录加入 sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import config
from utils.logger import get_logger
from database.mysql_client import test_connection, engine
from graph.neo4j_client import close_driver

logger = get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期: 启动时初始化, 关闭时清理"""
    logger.info("=== {} v{} 启动中 ===", config.APP_TITLE, config.APP_VERSION)
    await test_connection()
    yield
    # 关闭连接
    await engine.dispose()
    await close_driver()
    logger.info("=== 应用已关闭 ===")


app = FastAPI(
    title=config.APP_TITLE,
    version=config.APP_VERSION,
    description="知识图谱 + RAG智能问答 + 数字教师 数据分析平台",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件
app.mount("/static", StaticFiles(directory=str(config.STATIC_DIR)), name="static")

# 注册路由
from api.v1 import auth, graph, qa, teacher, dashboard, files, system

app.include_router(auth.router, prefix="/api/v1/auth", tags=["用户认证"])
app.include_router(graph.router, prefix="/api/v1/graph", tags=["知识图谱"])
app.include_router(qa.router, prefix="/api/v1/qa", tags=["智能问答"])
app.include_router(teacher.router, prefix="/api/v1/teacher", tags=["数字教师"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["数据分析"])
app.include_router(files.router, prefix="/api/v1/files", tags=["文件管理"])
app.include_router(system.router, prefix="/api/v1/system", tags=["系统管理"])


@app.get("/", tags=["默认"])
async def root():
    return {
        "name": config.APP_TITLE,
        "version": config.APP_VERSION,
        "docs": "/docs",
        "endpoints": {
            "auth": "/api/v1/auth",
            "graph": "/api/v1/graph",
            "qa": "/api/v1/qa",
            "teacher": "/api/v1/teacher",
            "dashboard": "/api/v1/dashboard",
            "files": "/api/v1/files",
            "system": "/api/v1/system",
        }
    }


@app.get("/health", tags=["默认"])
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
