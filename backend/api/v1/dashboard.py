"""数据分析路由 — /api/v1/dashboard"""
from fastapi import APIRouter, Depends, Query
from api.deps import get_current_user
from models.schemas import UserOut
from service import analysis_service
from utils.response import success, error

router = APIRouter()


@router.get("/overview")
async def overview():
    try:
        data = await analysis_service.get_overview()
        return success(data)
    except Exception as e:
        return error(500, f"获取概览失败: {e}")


@router.get("/question-trend")
async def question_trend(
    start_date: str = Query(...),
    end_date: str = Query(...),
    course: str = Query(default=None),
    granularity: str = Query(default="day"),
):
    try:
        data = await analysis_service.get_question_trend(start_date, end_date, course, granularity)
        return success(data)
    except Exception as e:
        return error(500, f"获取趋势失败: {e}")


@router.get("/topic-heatmap")
async def topic_heatmap(course: str = Query(default=None)):
    try:
        data = await analysis_service.get_topic_heatmap(course)
        return success(data)
    except Exception as e:
        return error(500, f"获取热度失败: {e}")


@router.get("/user-activity")
async def user_activity(start_date: str = Query(...), end_date: str = Query(...)):
    try:
        data = await analysis_service.get_user_activity(start_date, end_date)
        return success(data)
    except Exception as e:
        return error(500, f"获取活跃度失败: {e}")


@router.get("/satisfaction")
async def satisfaction():
    try:
        data = await analysis_service.get_satisfaction()
        return success(data)
    except Exception as e:
        return error(500, f"获取满意度失败: {e}")


@router.get("/mastery-radar")
async def mastery_radar(user: UserOut = Depends(get_current_user)):
    try:
        data = await analysis_service.get_mastery_radar(user.user_id)
        return success(data)
    except Exception as e:
        return error(500, f"获取掌握度失败: {e}")
