"""系统管理服务层 — 健康检查、模型状态、配置管理"""
import os
from sqlalchemy import text
from database.mysql_client import AsyncSessionLocal
from service.llm_service import check_ollama_status
from graph.neo4j_client import get_driver
from rag.vector_store import get_index_info
import config
from utils.logger import get_logger

logger = get_logger()


async def health_check() -> dict:
    """系统健康检查"""
    services = {}

    # MySQL
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        services["mysql"] = {"status": "up"}
    except Exception as e:
        services["mysql"] = {"status": "down", "error": str(e)}

    # Neo4j
    try:
        driver = await get_driver()
        async with driver.session(database=config.NEO4J_DATABASE) as session:
            await session.run("RETURN 1")
        services["neo4j"] = {"status": "up"}
    except Exception as e:
        services["neo4j"] = {"status": "down", "error": str(e)}

    # Ollama
    ollama = await check_ollama_status()
    services["ollama"] = ollama

    # FAISS
    try:
        info = get_index_info()
        services["faiss"] = {"status": "up", "vectors": info["total_vectors"]}
    except Exception as e:
        services["faiss"] = {"status": "down", "error": str(e)}

    # GPU (懒加载 torch，避免未安装时崩溃)
    gpu = {}
    try:
        import torch
        if torch.cuda.is_available():
            gpu = {
                "device": torch.cuda.get_device_name(0),
                "total_memory_gb": round(torch.cuda.get_device_properties(0).total_memory / 1e9, 1),
                "used_memory_gb": round(torch.cuda.memory_allocated() / 1e9, 1),
                "free_memory_gb": round((torch.cuda.get_device_properties(0).total_memory - torch.cuda.memory_allocated()) / 1e9, 1),
            }
        else:
            gpu = {"device": "CPU", "total_memory_gb": 0, "used_memory_gb": 0, "free_memory_gb": 0}
    except ImportError:
        gpu = {"device": "CPU", "total_memory_gb": 0, "used_memory_gb": 0, "free_memory_gb": 0}

    all_up = all(s.get("status") == "up" for s in services.values())
    return {
        "status": "healthy" if all_up else "degraded",
        "services": services,
        "gpu": gpu,
        "strategy": f"GPU交替加载: {config.GPU_STRATEGY}",
    }


async def model_status() -> dict:
    """大模型状态"""
    ollama = await check_ollama_status()
    faiss_info = get_index_info()

    return {
        "llm": {
            "name": config.OLLAMA_MODEL,
            "provider": "ollama",
            "status": "loaded" if ollama.get("model_loaded") else "not_loaded",
            "available_models": ollama.get("models", []),
        },
        "embedding": {
            "name": config.EMBEDDING_MODEL,
            "dimension": config.EMBEDDING_DIM,
        },
        "faiss": faiss_info,
        "tts": {
            "name": "IndexTTS2",
            "checkpoints": config.INDEXTTS_CHECKPOINTS,
            "available": os.path.exists(config.INDEXTTS_CFG),
            "voice_prompt": config.INDEXTTS_VOICE_PROMPT,
            "use_fp16": config.INDEXTTS_USE_FP16,
        },
        "gpu": {
            "total_memory_gb": config.GPU_TOTAL_MEMORY_GB,
            "strategy": config.GPU_STRATEGY,
            "note": "DeepSeek(4.5GB)与IndexTTS2/SD(3.5GB)交替加载，不同时满载"
        }
    }


async def get_config() -> dict:
    """获取系统配置"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("SELECT config_key, config_value, value_type, description, is_editable FROM system_config ORDER BY config_key"))
        rows = result.mappings().all()
        config_dict = {}
        for r in rows:
            try:
                import json
                val = json.loads(r["config_value"])
            except Exception:
                val = r["config_value"]
            config_dict[r["config_key"]] = {
                "value": val,
                "type": r["value_type"],
                "description": r["description"],
                "editable": r["is_editable"],
            }
        return config_dict


async def update_config(key: str, value: str, user_id: int) -> bool:
    """更新系统配置"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("SELECT is_editable FROM system_config WHERE config_key = :k"),
            {"k": key}
        )
        row = result.mappings().first()
        if not row:
            return False
        if not row["is_editable"]:
            raise ValueError(f"配置项 {key} 不可编辑")

        import json
        if not value.startswith('"'):
            value = json.dumps(value, ensure_ascii=False)

        await db.execute(
            text("UPDATE system_config SET config_value = :v, updated_by = :uid WHERE config_key = :k"),
            {"v": value, "uid": user_id, "k": key}
        )
        await db.commit()
        return True


async def get_announcements() -> list:
    """获取系统公告"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("""
            SELECT announcement_id, title, content, type, is_pinned, created_at
            FROM system_announcements
            WHERE is_active = TRUE
            ORDER BY is_pinned DESC, created_at DESC
        """))
        return [dict(r) for r in result.mappings()]
