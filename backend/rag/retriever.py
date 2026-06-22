"""RAG 检索器 — 双路检索: FAISS 向量 + Neo4j 图谱"""
import json
import httpx
from typing import Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from database.mysql_client import get_db, AsyncSessionLocal
from rag.vector_store import embed_query, search_vectors, get_index_info
from rag.document_processor import chunk_text, extract_text, get_file_type
from service.graph_service import get_node_context_for_rag
import config
from utils.logger import get_logger

logger = get_logger()


async def retrieve_from_faiss(question: str, top_k: int = 5, db: AsyncSession = None) -> list:
    """向量检索: FAISS + MySQL 分块内容"""
    try:
        query_vec = embed_query(question)
        indices, scores = search_vectors(query_vec, top_k)
        if not indices:
            return []

        # 从 MySQL 获取分块内容
        if db is None:
            async with AsyncSessionLocal() as session:
                return await _fetch_chunks(session, indices, scores)
        return await _fetch_chunks(db, indices, scores)
    except Exception as e:
        logger.error("FAISS 检索失败: {}", e)
        return []


async def _fetch_chunks(db: AsyncSession, indices: list, scores: list) -> list:
    """根据 FAISS 索引从 MySQL 获取分块内容"""
    results = []
    for idx, score in zip(indices, scores):
        if score < config.RAG_SIMILARITY_THRESHOLD:
            continue
        row = await db.execute(
            text("""SELECT fc.content, fc.start_page, kf.filename AS source, kf.course
                    FROM file_chunks fc
                    JOIN knowledge_files kf ON fc.file_id = kf.file_id
                    WHERE fc.faiss_index = :idx"""),
            {"idx": idx}
        )
        r = row.mappings().first()
        if r:
            results.append({
                "source": r["source"],
                "page": r["start_page"],
                "content": r["content"][:500],
                "score": float(score),
            })
    return results


async def retrieve_from_graph(question: str, keywords: list = None) -> dict:
    """图谱检索: 从 Neo4j 提取相关知识上下文"""
    try:
        if not keywords:
            # 简单关键词提取: 取问题中的名词（2-4字中文词）
            keywords = _extract_keywords(question)
        return await get_node_context_for_rag(keywords)
    except Exception as e:
        logger.error("图谱检索失败: {}", e)
        return {"related_nodes": [], "relations": []}


def _extract_keywords(question: str) -> list:
    """简单关键词提取（基于规则）"""
    # 去除常见停用词
    stop_words = {"什么", "是", "的", "了", "吗", "呢", "啊", "如何", "怎么", "为什么", "哪些", "哪个", "请", "解释", "说明", "介绍"}
    words = question.replace("？", "").replace("？", "").replace(",", " ").replace("，", " ").split()
    keywords = [w for w in words if w not in stop_words and len(w) >= 2]

    # 如果没有分词结果，直接用原问题
    if not keywords:
        keywords = [question.strip()]

    return keywords[:5]


async def build_prompt(question: str, references: list, graph_context: dict, history: list = None) -> str:
    """拼接 RAG Prompt"""
    context_parts = []

    # 文档检索结果
    if references:
        doc_text = "\n\n".join(
            f"[参考文档{i+1}] (来源: {r['source']}, 相似度: {r['score']:.2f})\n{r['content']}"
            for i, r in enumerate(references)
        )
        context_parts.append(doc_text)

    # 图谱上下文
    if graph_context.get("related_nodes"):
        graph_text = f"[知识图谱关联知识点]\n相关知识点: {', '.join(graph_context['related_nodes'])}"
        if graph_context.get("relations"):
            graph_text += f"\n知识关系: {'; '.join(graph_context['relations'])}"
        context_parts.append(graph_text)

    # 历史对话
    if history:
        history_text = "\n".join(
            f"{'用户' if m['role'] == 'user' else 'AI'}: {m['content'][:200]}"
            for m in history[-6:]  # 最近3轮
        )
        context_parts.append(f"[对话历史]\n{history_text}")

    context = "\n\n---\n\n".join(context_parts) if context_parts else "（无额外上下文）"

    prompt = f"""你是一个专业的课程知识助教，请基于以下参考信息回答学生的问题。

{context}

---

学生问题: {question}

请根据参考信息回答，如果参考信息不足可以结合自身知识补充，但需明确标注哪些是参考资料中的内容。回答要简洁清晰，适合学生理解。"""

    return prompt
