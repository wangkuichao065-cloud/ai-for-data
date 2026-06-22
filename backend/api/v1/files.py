"""文件管理路由 — /api/v1/files"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, Query
from api.deps import get_current_user, require_role
from models.schemas import UserOut
from service import file_service
from utils.response import success, error, paginate

router = APIRouter()


@router.post("/upload")
async def upload(
    file: UploadFile = File(...),
    course: str = Form(...),
    category: str = Form(default=None),
    description: str = Form(default=None),
    user: UserOut = Depends(require_role("teacher", "admin")),
):
    """上传知识库文档"""
    try:
        content = await file.read()
        data = await file_service.upload_file(content, file.filename, course, category, description, user.user_id)
        if data.get("status") == "duplicate":
            return error(409, "文件已存在", data)
        return success(data, "文件上传成功")
    except Exception as e:
        return error(500, f"上传失败: {e}")


@router.get("/{file_id}/status")
async def status(file_id: str):
    try:
        data = await file_service.get_file_status(file_id)
        if not data:
            return error(404, "文件不存在")
        return success(data)
    except Exception as e:
        return error(500, f"获取状态失败: {e}")


@router.get("/{file_id}")
async def file_detail(file_id: str, user: UserOut = Depends(get_current_user)):
    """获取文件完整详情"""
    try:
        data = await file_service.get_file_detail(file_id)
        if not data:
            return error(404, "文件不存在")
        return success(data)
    except Exception as e:
        return error(500, f"获取文件详情失败: {e}")


@router.get("")
async def list_files(course: str = Query(default=None), page: int = Query(1), page_size: int = Query(20)):
    try:
        data = await file_service.list_files(course, page, page_size)
        return paginate(data["list"], data["total"], data["page"], data["page_size"])
    except Exception as e:
        return error(500, f"获取文件列表失败: {e}")


@router.delete("/{file_id}")
async def delete_file(file_id: str, user: UserOut = Depends(require_role("teacher", "admin"))):
    try:
        deleted = await file_service.delete_file(file_id)
        if not deleted:
            return error(404, "文件不存在")
        return success(message="文件已删除")
    except Exception as e:
        return error(500, f"删除失败: {e}")


@router.post("/rebuild-index")
async def rebuild_index(user: UserOut = Depends(require_role("admin"))):
    try:
        data = await file_service.rebuild_index()
        return success(data, "索引重建完成")
    except Exception as e:
        return error(500, f"索引重建失败: {e}")
