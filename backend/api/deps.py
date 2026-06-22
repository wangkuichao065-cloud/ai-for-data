"""FastAPI 依赖注入 — 获取当前用户、角色校验"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from database.mysql_client import get_db
from utils.jwt import decode_token
from models.schemas import UserOut

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    """从 JWT Token 解析当前登录用户"""
    if not credentials:
        raise HTTPException(status_code=401, detail="未提供认证Token")
    
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Token无效或已过期")
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token内容无效")
    
    result = await db.execute(
        text("SELECT user_id, username, email, phone, nickname, role, avatar, login_count, last_login FROM users WHERE user_id = :uid AND status = 1"),
        {"uid": user_id}
    )
    row = result.mappings().first()
    if not row:
        raise HTTPException(status_code=401, detail="用户不存在或已禁用")
    
    return UserOut(
        user_id=row["user_id"], username=row["username"], email=row["email"],
        phone=row["phone"], nickname=row["nickname"], role=row["role"],
        avatar=row["avatar"], login_count=row["login_count"],
        last_login=str(row["last_login"]) if row["last_login"] else None
    )


def require_role(*roles: str):
    """角色权限校验依赖"""
    async def checker(user: UserOut = Depends(get_current_user)) -> UserOut:
        if user.role not in roles:
            raise HTTPException(status_code=403, detail=f"需要 {', '.join(roles)} 权限")
        return user
    return checker
