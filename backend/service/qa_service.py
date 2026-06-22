"""智能问答服务层 — RAG 双路检索 + DeepSeek 生成"""
import time
import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from database.mysql_client import AsyncSessionLocal
from rag.retriever import retrieve_from_faiss, retrieve_from_graph, build_prompt, _extract_keywords
from service.llm_service import stream_chat, chat
from utils.logger import get_logger

logger = get_logger()


async def _get_or_create_session(session_id: str, user_id: int, course: str, db: AsyncSession) -> str:
    """获取或创建会话"""
    if session_id:
        return session_id
    session_id = f"sess_{uuid.uuid4().hex[:16]}"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    await db.execute(
        text("""INSERT INTO chat_sessions (session_id, user_id, title, course, created_at, updated_at)
                VALUES (:sid, :uid, :title, :course, :t, :t)"""),
        {"sid": session_id, "uid": user_id, "title": "新对话", "course": course, "t": now}
    )
    await db.commit()
    return session_id


async def _save_messages(session_id: str, user_id: int, question: str, answer: str, db: AsyncSession):
    """保存用户问题和AI回答到消息表"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    await db.execute(
        text("INSERT INTO chat_messages (session_id, role, content, content_type, created_at) VALUES (:sid, 'user', :c, 'text', :t)"),
        {"sid": session_id, "c": question, "t": now}
    )
    await db.execute(
        text("INSERT INTO chat_messages (session_id, role, content, content_type, model_name, created_at) VALUES (:sid, 'assistant', :c, 'markdown', :m, :t)"),
        {"sid": session_id, "c": answer, "m": "deepseek-r1:7b", "t": now}
    )
    await db.execute(
        text("UPDATE chat_sessions SET message_count = message_count + 2, updated_at = :t WHERE session_id = :sid"),
        {"sid": session_id, "t": now}
    )
    await db.commit()


async def _save_answer(session_id: str, user_id: int, question: str, answer: str,
                       course: str, references: list, graph_context: dict,
                       usage: dict, response_time_ms: int, db: AsyncSession) -> str:
    """保存问答记录"""
    answer_id = f"ans_{uuid.uuid4().hex[:16]}"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    await db.execute(
        text("""INSERT INTO qa_answers
                (answer_id, session_id, user_id, question, answer, course, enable_rag, enable_graph,
                 references_json, graph_context_json, related_nodes_json, model_name, temperature,
                 prompt_tokens, completion_tokens, total_tokens, response_time_ms, is_streaming, created_at)
                VALUES (:aid, :sid, :uid, :q, :a, :course, TRUE, TRUE, :refs, :gctx, :nodes,
                        'deepseek-r1:7b', 0.7, :pt, :ct, :tt, :rt, FALSE, :t)"""),
        {
            "aid": answer_id, "sid": session_id, "uid": user_id, "q": question, "a": answer,
            "course": course, "refs": json.dumps(references, ensure_ascii=False),
            "gctx": json.dumps(graph_context, ensure_ascii=False),
            "nodes": json.dumps(graph_context.get("related_nodes", []), ensure_ascii=False),
            "pt": usage.get("prompt_tokens", 0), "ct": usage.get("completion_tokens", 0),
            "tt": usage.get("total_tokens", 0), "rt": response_time_ms, "t": now
        }
    )
    await db.commit()
    return answer_id


async def ask_sync(question: str, user_id: int, course: str = None, session_id: str = None,
                   enable_rag: bool = True, enable_graph: bool = True, top_k: int = 5) -> dict:
    """非流式问答"""
    start = time.time()

    async with AsyncSessionLocal() as db:
        session_id = await _get_or_create_session(session_id, user_id, course, db)

        # 双路检索
        references = []
        graph_context = {"related_nodes": [], "relations": []}

        if enable_rag:
            references = await retrieve_from_faiss(question, top_k, db)
        if enable_graph:
            keywords = _extract_keywords(question)
            graph_context = await retrieve_from_graph(question, keywords)

        # 获取历史对话
        history_result = await db.execute(
            text("""SELECT role, content FROM chat_messages WHERE session_id = :sid ORDER BY created_at DESC LIMIT 6"""),
            {"sid": session_id}
        )
        history = [dict(r) for r in history_result.mappings()]
        history.reverse()

        # 构建 Prompt 并调用 LLM
        prompt = await build_prompt(question, references, graph_context, history)
        result = await chat(prompt)

        answer = result["answer"]
        usage = result["usage"]
        response_time_ms = int((time.time() - start) * 1000)

        # 保存
        await _save_messages(session_id, user_id, question, answer, db)
        answer_id = await _save_answer(session_id, user_id, question, answer, course,
                                       references, graph_context, usage, response_time_ms, db)

        return {
            "answer_id": answer_id,
            "session_id": session_id,
            "question": question,
            "answer": answer,
            "references": references,
            "graph_context": graph_context,
            "usage": usage,
            "response_time_ms": response_time_ms,
        }


async def ask_stream(question: str, user_id: int, course: str = None, session_id: str = None,
                     enable_rag: bool = True, enable_graph: bool = True, top_k: int = 5):
    """流式问答 — 异步生成器，yield SSE 事件"""
    start = time.time()

    async with AsyncSessionLocal() as db:
        session_id = await _get_or_create_session(session_id, user_id, course, db)

        # 检索阶段
        yield {"type": "status", "message": "正在检索知识库..."}

        references = []
        graph_context = {"related_nodes": [], "relations": []}

        if enable_rag:
            references = await retrieve_from_faiss(question, top_k, db)
            yield {"type": "references", "data": references}
        if enable_graph:
            keywords = _extract_keywords(question)
            graph_context = await retrieve_from_graph(question, keywords)
            yield {"type": "graph_context", "data": graph_context}

        # 获取历史
        history_result = await db.execute(
            text("SELECT role, content FROM chat_messages WHERE session_id = :sid ORDER BY created_at DESC LIMIT 6"),
            {"sid": session_id}
        )
        history = [dict(r) for r in history_result.mappings()]
        history.reverse()

        # 构建 Prompt
        prompt = await build_prompt(question, references, graph_context, history)

        yield {"type": "status", "message": "正在生成回答..."}

        # 流式生成
        full_answer = ""
        usage = {}
        async for event in stream_chat(prompt):
            if event["type"] == "token":
                full_answer += event["content"]
                yield event
            elif event["type"] == "done":
                usage = event["usage"]
                yield event
            elif event["type"] == "error":
                yield event
                return

        response_time_ms = int((time.time() - start) * 1000)

        # 保存
        await _save_messages(session_id, user_id, question, full_answer, db)
        answer_id = await _save_answer(session_id, user_id, question, full_answer, course,
                                       references, graph_context, usage, response_time_ms, db)

        yield {"type": "finished", "answer_id": answer_id, "session_id": session_id, "response_time_ms": response_time_ms}


async def get_session_history(session_id: str, page: int = 1, page_size: int = 20) -> dict:
    """获取会话问答历史"""
    async with AsyncSessionLocal() as db:
        offset = (page - 1) * page_size
        result = await db.execute(
            text("""SELECT answer_id, question, answer, created_at FROM qa_answers
                    WHERE session_id = :sid ORDER BY created_at DESC LIMIT :limit OFFSET :offset"""),
            {"sid": session_id, "limit": page_size, "offset": offset}
        )
        items = [dict(r) for r in result.mappings()]
        count_result = await db.execute(
            text("SELECT COUNT(*) AS total FROM qa_answers WHERE session_id = :sid"),
            {"sid": session_id}
        )
        total = count_result.scalar()
        return {"list": items, "total": total, "page": page, "page_size": page_size}


async def get_user_sessions(user_id: int) -> list:
    """获取用户会话列表"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("""SELECT s.session_id, s.title, s.course, s.message_count, s.created_at, s.updated_at,
                    (SELECT content FROM chat_messages WHERE session_id = s.session_id ORDER BY created_at DESC LIMIT 1) AS last_message
                    FROM chat_sessions s WHERE s.user_id = :uid AND s.status = 1 ORDER BY s.updated_at DESC"""),
            {"uid": user_id}
        )
        return [dict(r) for r in result.mappings()]


async def create_session(user_id: int, title: str, course: str = None) -> dict:
    """创建新会话"""
    session_id = f"sess_{uuid.uuid4().hex[:16]}"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    async with AsyncSessionLocal() as db:
        await db.execute(
            text("INSERT INTO chat_sessions (session_id, user_id, title, course, created_at, updated_at) VALUES (:sid, :uid, :t, :c, :now, :now)"),
            {"sid": session_id, "uid": user_id, "t": title, "c": course, "now": now}
        )
        await db.commit()
    return {"session_id": session_id, "title": title, "course": course}


async def delete_session(session_id: str, user_id: int):
    """删除会话（软删除）"""
    async with AsyncSessionLocal() as db:
        await db.execute(
            text("UPDATE chat_sessions SET status = 0 WHERE session_id = :sid AND user_id = :uid"),
            {"sid": session_id, "uid": user_id}
        )
        await db.commit()


async def save_feedback(answer_id: str, user_id: int, rating: int, is_helpful: bool, comment: str):
    """保存回答反馈"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    async with AsyncSessionLocal() as db:
        await db.execute(
            text("""INSERT INTO user_feedback (answer_id, user_id, rating, is_helpful, comment, created_at)
                    VALUES (:aid, :uid, :r, :h, :c, :t)
                    ON DUPLICATE KEY UPDATE rating = :r, is_helpful = :h, comment = :c"""),
            {"aid": answer_id, "uid": user_id, "r": rating, "h": is_helpful, "c": comment, "t": now}
        )
        await db.commit()


async def get_rag_status() -> dict:
    """RAG 知识库状态"""
    from rag.vector_store import get_index_info
    info = get_index_info()
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("SELECT COUNT(*) AS files FROM knowledge_files WHERE status = 'completed'")
        )
        info["total_documents"] = result.scalar()
        result = await db.execute(text("SELECT COUNT(*) AS chunks FROM file_chunks"))
        info["total_chunks"] = result.scalar()
    return info
