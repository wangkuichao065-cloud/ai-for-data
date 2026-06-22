"""智能问答路由 — /api/v1/qa"""
import json
import asyncio
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from database.mysql_client import get_db
from api.deps import get_current_user
from models.schemas import QARequest, SessionCreate, FeedbackRequest, UserOut
from service import qa_service
from utils.response import success, error, paginate

router = APIRouter()


@router.post("/ask")
async def ask(req: QARequest, user: UserOut = Depends(get_current_user)):
    """流式问答（SSE）"""
    async def event_stream():
        try:
            async for event in qa_service.ask_stream(
                req.question, user.user_id, req.course, req.session_id,
                req.enable_rag, req.enable_graph, req.top_k
            ):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/ask-sync")
async def ask_sync(req: QARequest, user: UserOut = Depends(get_current_user)):
    """非流式问答"""
    try:
        data = await qa_service.ask_sync(
            req.question, user.user_id, req.course, req.session_id,
            req.enable_rag, req.enable_graph, req.top_k
        )
        return success(data)
    except Exception as e:
        return error(500, f"问答失败: {e}")


@router.get("/history/{session_id}")
async def history(session_id: str, page: int = Query(1), page_size: int = Query(20)):
    try:
        data = await qa_service.get_session_history(session_id, page, page_size)
        return paginate(data["list"], data["total"], data["page"], data["page_size"])
    except Exception as e:
        return error(500, f"获取历史失败: {e}")


@router.get("/sessions")
async def sessions(user: UserOut = Depends(get_current_user)):
    try:
        data = await qa_service.get_user_sessions(user.user_id)
        return success(data)
    except Exception as e:
        return error(500, f"获取会话列表失败: {e}")


@router.post("/sessions")
async def create_session(req: SessionCreate, user: UserOut = Depends(get_current_user)):
    try:
        data = await qa_service.create_session(user.user_id, req.title, req.course)
        return success(data, "会话创建成功")
    except Exception as e:
        return error(500, f"创建会话失败: {e}")


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str, user: UserOut = Depends(get_current_user)):
    try:
        await qa_service.delete_session(session_id, user.user_id)
        return success(message="会话已删除")
    except Exception as e:
        return error(500, f"删除失败: {e}")


@router.get("/answers/{answer_id}")
async def answer_detail(answer_id: str, db: AsyncSession = Depends(get_db)):
    try:
        from sqlalchemy import text
        result = await db.execute(
            text("""SELECT answer_id, session_id, question, answer, course, enable_rag, enable_graph,
                    references_json, graph_context_json, model_name, temperature,
                    prompt_tokens, completion_tokens, response_time_ms, created_at
                    FROM qa_answers WHERE answer_id = :aid"""),
            {"aid": answer_id}
        )
        row = result.mappings().first()
        if not row:
            return error(404, "回答不存在")
        import json as _json
        data = dict(row)
        data["references"] = _json.loads(data.pop("references_json")) if data.get("references_json") else []
        data["graph_context"] = _json.loads(data.pop("graph_context_json")) if data.get("graph_context_json") else {}
        return success(data)
    except Exception as e:
        return error(500, f"获取回答详情失败: {e}")


@router.post("/answers/{answer_id}/feedback")
async def feedback(answer_id: str, req: FeedbackRequest, user: UserOut = Depends(get_current_user)):
    try:
        await qa_service.save_feedback(answer_id, user.user_id, req.rating, req.is_helpful, req.comment)
        return success(message="反馈已提交")
    except Exception as e:
        return error(500, f"提交反馈失败: {e}")


@router.get("/rag/status")
async def rag_status():
    try:
        data = await qa_service.get_rag_status()
        return success(data)
    except Exception as e:
        return error(500, f"获取RAG状态失败: {e}")
