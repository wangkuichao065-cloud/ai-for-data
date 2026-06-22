"""用户认证服务层"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from utils.jwt import hash_password, verify_password, create_access_token, create_refresh_token
from utils.logger import get_logger
from models.schemas import RegisterRequest, LoginRequest, UserOut

logger = get_logger()


async def register_user(req: RegisterRequest, db: AsyncSession) -> dict:
    """用户注册"""
    existing = await db.execute(
        text("SELECT user_id FROM users WHERE username = :u OR email = :e"),
        {"u": req.username, "e": req.email}
    )
    if existing.first():
        raise ValueError("用户名或邮箱已存在")

    hashed = hash_password(req.password)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    result = await db.execute(
        text("""INSERT INTO users (username, password, email, role, created_at, updated_at)
                VALUES (:u, :p, :e, :r, :t, :t)"""),
        {"u": req.username, "p": hashed, "e": req.email, "r": req.role, "t": now}
    )
    await db.commit()
    user_id = result.lastrowid
    logger.info("新用户注册: id={}, username={}", user_id, req.username)
    return {"user_id": user_id, "username": req.username, "role": req.role, "created_at": now}


async def login_user(req: LoginRequest, db: AsyncSession, client_ip: str = "") -> dict:
    """用户登录，返回 JWT Token"""
    result = await db.execute(
        text("SELECT user_id, username, password, email, phone, nickname, role, avatar, login_count, status FROM users WHERE username = :u"),
        {"u": req.username}
    )
    row = result.mappings().first()
    if not row or not verify_password(req.password, row["password"]):
        raise ValueError("用户名或密码错误")
    if row["status"] != 1:
        raise ValueError("账号已被禁用")

    user_data = {"user_id": row["user_id"], "username": row["username"], "role": row["role"]}
    token = create_access_token(user_data)
    refresh = create_refresh_token(user_data)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    await db.execute(
        text("UPDATE users SET login_count = login_count + 1, last_login = :t, last_login_ip = :ip WHERE user_id = :uid"),
        {"t": now, "ip": client_ip, "uid": row["user_id"]}
    )
    await db.commit()

    logger.info("用户登录: id={}, username={}", row["user_id"], row["username"])
    return {
        "token": token,
        "refresh_token": refresh,
        "expires_in": 7200,
        "user": {
            "user_id": row["user_id"],
            "username": row["username"],
            "email": row["email"],
            "phone": row["phone"],
            "nickname": row["nickname"],
            "role": row["role"],
            "avatar": row["avatar"],
        }
    }


async def refresh_token_service(refresh: str, db: AsyncSession) -> dict:
    """刷新 Token"""
    from utils.jwt import decode_token
    payload = decode_token(refresh)
    if not payload or payload.get("type") != "refresh":
        raise ValueError("Refresh Token 无效")

    user_data = {"user_id": payload["user_id"], "username": payload["username"], "role": payload["role"]}
    result = await db.execute(
        text("SELECT status FROM users WHERE user_id = :uid"),
        {"uid": payload["user_id"]}
    )
    row = result.mappings().first()
    if not row or row["status"] != 1:
        raise ValueError("用户不存在或已禁用")

    new_token = create_access_token(user_data)
    new_refresh = create_refresh_token(user_data)
    return {"token": new_token, "refresh_token": new_refresh, "expires_in": 7200}


async def change_password(user_id: int, old_pw: str, new_pw: str, db: AsyncSession):
    """修改密码"""
    result = await db.execute(text("SELECT password FROM users WHERE user_id = :uid"), {"uid": user_id})
    row = result.mappings().first()
    if not row or not verify_password(old_pw, row["password"]):
        raise ValueError("原密码错误")

    await db.execute(
        text("UPDATE users SET password = :p WHERE user_id = :uid"),
        {"p": hash_password(new_pw), "uid": user_id}
    )
    await db.commit()
    logger.info("用户修改密码: id={}", user_id)
