"""用户认证路由 — /api/v1/auth"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from database.mysql_client import get_db
from models.schemas import RegisterRequest, LoginRequest, RefreshRequest, PasswordChangeRequest
from api.deps import get_current_user
from service import auth_service
from utils.response import success, error
from models.schemas import UserOut

router = APIRouter()


@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        data = await auth_service.register_user(req, db)
        return success(data, "注册成功")
    except ValueError as e:
        return error(409, str(e))
    except Exception as e:
        return error(500, f"注册失败: {e}")


@router.post("/login")
async def login(req: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        client_ip = request.client.host if request.client else ""
        data = await auth_service.login_user(req, db, client_ip)
        return success(data, "登录成功")
    except ValueError as e:
        return error(401, str(e))
    except Exception as e:
        return error(500, f"登录失败: {e}")


@router.post("/refresh")
async def refresh(req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    try:
        data = await auth_service.refresh_token_service(req.refresh_token, db)
        return success(data, "刷新成功")
    except ValueError as e:
        return error(401, str(e))


@router.get("/me")
async def me(user: UserOut = Depends(get_current_user)):
    return success(user.model_dump())


@router.put("/password")
async def change_password(req: PasswordChangeRequest, user: UserOut = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    try:
        await auth_service.change_password(user.user_id, req.old_password, req.new_password, db)
        return success(message="密码修改成功")
    except ValueError as e:
        return error(400, str(e))
