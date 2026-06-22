"""统一响应格式"""
from typing import Any, Optional
from datetime import datetime, timezone


def success(data: Any = None, message: str = "success"):
    return {"code": 200, "message": message, "data": data, "timestamp": datetime.now(timezone.utc).isoformat()}


def error(code: int = 400, message: str = "error", data: Any = None):
    return {"code": code, "message": message, "data": data, "timestamp": datetime.now(timezone.utc).isoformat()}


def paginate(list_data: list, total: int, page: int, page_size: int):
    return success({"list": list_data, "total": total, "page": page, "page_size": page_size})
