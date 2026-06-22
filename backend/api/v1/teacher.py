"""数字教师路由 — /api/v1/teacher"""
from fastapi import APIRouter, Depends
from api.deps import get_current_user
from models.schemas import TeacherChatRequest, TTSRequest, UserOut
from service import teacher_service, tts_service
from utils.response import success, error

router = APIRouter()


@router.post("/chat")
async def chat(req: TeacherChatRequest, user: UserOut = Depends(get_current_user)):
    """数字教师对话"""
    try:
        data = await teacher_service.teacher_chat(
            req.question, user.user_id, req.session_id, req.enable_voice, req.emotion
        )
        return success(data)
    except Exception as e:
        return error(500, f"数字教师对话失败: {e}")


@router.get("/avatar")
async def avatar(emotion: str = "normal"):
    """获取数字教师形象资源"""
    emotions = {
        "normal": "/static/teacher/normal.png",
        "happy": "/static/teacher/happy.png",
        "serious": "/static/teacher/serious.png",
        "thinking": "/static/teacher/thinking.png",
    }
    return success({
        "model_url": "/static/teacher/model.json",
        "current_emotion": emotion,
        "textures": [
            {"emotion": e, "url": url}
            for e, url in emotions.items()
        ],
    })


@router.post("/tts")
async def tts(req: TTSRequest, user: UserOut = Depends(get_current_user)):
    """文字转语音"""
    try:
        data = await tts_service.generate_speech(req.text, req.voice, req.speed)
        return success(data)
    except Exception as e:
        return error(500, f"语音合成失败: {e}")


@router.get("/progress")
async def progress(user: UserOut = Depends(get_current_user)):
    """获取学习进度"""
    try:
        data = await teacher_service.get_teacher_progress(user.user_id)
        return success(data)
    except Exception as e:
        return error(500, f"获取进度失败: {e}")
