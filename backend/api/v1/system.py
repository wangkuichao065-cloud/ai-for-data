"""系统管理路由 — /api/v1/system"""
from fastapi import APIRouter, Depends, Query
from api.deps import get_current_user, require_role
from models.schemas import UserOut, ConfigUpdate
from service import system_service
from utils.response import success, error

router = APIRouter()


@router.get("/health")
async def health():
    try:
        data = await system_service.health_check()
        return success(data)
    except Exception as e:
        return error(503, f"健康检查失败: {e}")


@router.get("/model-status")
async def model_status():
    try:
        data = await system_service.model_status()
        return success(data)
    except Exception as e:
        return error(500, f"获取模型状态失败: {e}")


@router.get("/config")
async def get_config(user: UserOut = Depends(require_role("admin"))):
    try:
        data = await system_service.get_config()
        return success(data)
    except Exception as e:
        return error(500, f"获取配置失败: {e}")


@router.put("/config")
async def update_config(req: ConfigUpdate, key: str = Query(...), user: UserOut = Depends(require_role("admin"))):
    try:
        updated = await system_service.update_config(key, req.config_value, user.user_id)
        if not updated:
            return error(404, "配置项不存在")
        return success(message="配置已更新")
    except ValueError as e:
        return error(403, str(e))
    except Exception as e:
        return error(500, f"更新配置失败: {e}")


@router.get("/announcements")
async def announcements():
    try:
        data = await system_service.get_announcements()
        return success(data)
    except Exception as e:
        return error(500, f"获取公告失败: {e}")
