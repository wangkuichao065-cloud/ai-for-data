"""数字教师服务层 — RAG 问答 + 情绪判断 + TTS 语音"""
import uuid
import json
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from database.mysql_client import AsyncSessionLocal
from rag.retriever import retrieve_from_faiss, retrieve_from_graph, build_prompt, _extract_keywords
from service.llm_service import chat
from service.tts_service import generate_speech
from utils.logger import get_logger

logger = get_logger()

# 情绪 → IndexTTS2 emo_vector 映射
EMOTION_MAP = {
    "happy": "happy",
    "encouraging": "happy",
    "serious": "neutral",
    "thinking": "neutral",
    "normal": "neutral",
    "auto": None,  # 自动判断
}


def _detect_emotion(question: str) -> str:
    """简单情绪判断（基于关键词规则）"""
    if any(w in question for w in ["不懂", "不会", "难", "放弃", "太难"]):
        return "encouraging"
    if any(w in question for w in ["考试", "重点", "必考", "考点"]):
        return "serious"
    return "happy"


async def teacher_chat(question: str, user_id: int, session_id: str = None,
                       enable_voice: bool = False, emotion: str = "auto") -> dict:
    """数字教师对话"""
    async with AsyncSessionLocal() as db:
        # 检索
        references = await retrieve_from_faiss(question, 5, db)
        keywords = _extract_keywords(question)
        graph_context = await retrieve_from_graph(question, keywords)

        # 教师专用 Prompt
        prompt_parts = [
            "你是一位专业的课程教师，请用亲切、鼓励的语气回答学生的问题。",
            "回答要条理清晰，适合学生理解，可以适当举例说明。",
        ]
        if references:
            doc_text = "\n\n".join(f"[参考文档] (来源: {r['source']})\n{r['content']}" for r in references)
            prompt_parts.append(doc_text)
        if graph_context.get("related_nodes"):
            prompt_parts.append(f"[关联知识点] {', '.join(graph_context['related_nodes'])}")

        prompt_parts.append(f"\n学生问题: {question}\n\n请用教师口吻回答:")
        prompt = "\n\n".join(prompt_parts)

        # 调用 LLM
        result = await chat(prompt, temperature=0.7)
        answer = result["answer"]

        # 情绪判断
        detected_emotion = emotion
        if emotion == "auto":
            detected_emotion = _detect_emotion(question)
        action = "explain"
        if detected_emotion == "encouraging":
            action = "encourage"

        # TTS 语音合成
        voice_url = None
        duration_ms = 0
        if enable_voice:
            tts_result = await generate_speech(answer, emotion=EMOTION_MAP.get(detected_emotion))
            voice_url = tts_result.get("audio_url")
            duration_ms = tts_result.get("duration_ms", 0)

        # 保存到数字教师对话表
        msg_id = await _save_teacher_message(
            user_id, session_id, question, answer, detected_emotion, action,
            voice_url, duration_ms, references, db
        )

        return {
            "msg_id": msg_id,
            "answer": answer,
            "emotion": detected_emotion,
            "action": action,
            "voice_url": voice_url,
            "duration_ms": duration_ms,
            "references": references,
        }


async def _save_teacher_message(user_id: int, session_id: str, question: str, answer: str,
                                emotion: str, action: str, voice_url: str, duration_ms: int,
                                references: list, db: AsyncSession) -> int:
    """保存数字教师对话记录"""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    result = await db.execute(
        text("""INSERT INTO teacher_conversations
                (user_id, session_id, role, question, answer, emotion, action,
                 voice_url, voice_duration_ms, references_json, model_name, response_time_ms, created_at)
                VALUES (:uid, :sid, 'teacher', :q, :a, :emo, :act, :vurl, :vdur, :refs, 'deepseek-r1:7b', 0, :t)"""),
        {
            "uid": user_id, "sid": session_id, "q": question, "a": answer,
            "emo": emotion, "act": action, "vurl": voice_url, "vdur": duration_ms,
            "refs": json.dumps(references, ensure_ascii=False), "t": now
        }
    )
    await db.commit()
    return result.lastrowid


async def get_teacher_progress(user_id: int) -> dict:
    """获取学习进度"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("SELECT COUNT(*) AS total FROM teacher_conversations WHERE user_id = :uid"),
            {"uid": user_id}
        )
        total_questions = result.scalar()

        result = await db.execute(
            text("""SELECT DISTINCT course FROM teacher_conversations tc
                    JOIN chat_sessions cs ON tc.session_id = cs.session_id
                    WHERE tc.user_id = :uid AND cs.course IS NOT NULL"""),
            {"uid": user_id}
        )
        courses = [r["course"] for r in result.mappings()]

        result = await db.execute(
            text("""SELECT topic, mastery_level FROM study_progress
                    WHERE user_id = :uid AND mastery_level >= 0.7 ORDER BY mastery_level DESC"""),
            {"uid": user_id}
        )
        mastered = [r["topic"] for r in result.mappings()]

        result = await db.execute(
            text("""SELECT topic, mastery_level FROM study_progress
                    WHERE user_id = :uid AND mastery_level < 0.5 ORDER BY mastery_level ASC"""),
            {"uid": user_id}
        )
        weak = [r["topic"] for r in result.mappings()]

        result = await db.execute(
            text("SELECT COALESCE(SUM(study_duration_sec), 0) AS dur FROM study_progress WHERE user_id = :uid"),
            {"uid": user_id}
        )
        study_sec = result.scalar()

        level = "初级"
        if total_questions > 30:
            level = "高级"
        elif total_questions > 10:
            level = "中级"

        return {
            "total_questions": total_questions,
            "courses_covered": courses,
            "mastered_topics": mastered,
            "weak_topics": weak,
            "study_hours": round(study_sec / 3600, 1),
            "level": level,
        }
