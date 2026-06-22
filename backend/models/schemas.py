"""Pydantic 模型 — 请求/响应 Schema 定义"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


# ============================================================
# 用户认证
# ============================================================
class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, max_length=100)
    email: str
    role: str = Field(default="student")

class LoginRequest(BaseModel):
    username: str
    password: str

class RefreshRequest(BaseModel):
    refresh_token: str

class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

class ProfileUpdateRequest(BaseModel):
    nickname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    avatar: Optional[str] = None

class UserOut(BaseModel):
    user_id: int
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    nickname: Optional[str] = None
    role: str
    avatar: Optional[str] = None
    login_count: int = 0
    last_login: Optional[str] = None


# ============================================================
# 知识图谱
# ============================================================
class NodeCreate(BaseModel):
    label: str
    type: str
    course: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[int] = None
    importance: Optional[int] = None
    parent_id: Optional[str] = None

class EdgeCreate(BaseModel):
    source_id: str
    target_id: str
    relation: str
    properties: dict = {}


# ============================================================
# 智能问答
# ============================================================
class QARequest(BaseModel):
    question: str
    course: Optional[str] = None
    session_id: Optional[str] = None
    enable_rag: bool = True
    enable_graph: bool = True
    top_k: int = 5

class SessionCreate(BaseModel):
    title: str = "新对话"
    course: Optional[str] = None

class FeedbackRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    is_helpful: Optional[bool] = None
    comment: Optional[str] = None


# ============================================================
# 数字教师
# ============================================================
class TeacherChatRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    enable_voice: bool = False
    emotion: str = "auto"

class TTSRequest(BaseModel):
    text: str
    voice: str = "default"
    speed: float = 1.0

class AvatarGenerateRequest(BaseModel):
    prompt: str
    negative_prompt: str = "low quality, blurry, deformed"
    width: int = 512
    height: int = 512
    steps: int = 20
    cfg_scale: float = 7.5


# ============================================================
# 文件管理
# ============================================================
class FileUploadMeta(BaseModel):
    course: str
    category: Optional[str] = None
    description: Optional[str] = None


# ============================================================
# 系统配置
# ============================================================
class ConfigUpdate(BaseModel):
    config_value: str
