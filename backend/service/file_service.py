"""文件管理服务层 — 上传、分块、向量化、删除"""
import os
import uuid
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from database.mysql_client import AsyncSessionLocal
from rag.document_processor import extract_text, chunk_text, get_file_type
from rag.vector_store import embed_texts, add_vectors
import config
from utils.logger import get_logger

logger = get_logger()


async def upload_file(file_content: bytes, filename: str, course: str,
                      category: str = None, description: str = None,
                      uploaded_by: int = 1) -> dict:
    """上传文件并自动分块向量化"""
    file_type = get_file_type(filename)
    file_id = f"file_{uuid.uuid4().hex[:16]}"
    file_hash = hashlib.md5(file_content).hexdigest()

    # 检查重复
    async with AsyncSessionLocal() as db:
        existing = await db.execute(
            text("SELECT file_id FROM knowledge_files WHERE file_hash = :h"),
            {"h": file_hash}
        )
        if existing.first():
            return {"file_id": existing.first()[0], "status": "duplicate", "message": "文件已存在"}

    # 保存文件
    safe_name = f"{file_id}_{filename}"
    file_path = Path(config.UPLOAD_DIR) / safe_name
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(file_content)

    # 写入数据库
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    async with AsyncSessionLocal() as db:
        await db.execute(
            text("""INSERT INTO knowledge_files
                    (file_id, filename, file_path, file_type, file_size, file_hash, course, description, status, uploaded_by, created_at, updated_at)
                    VALUES (:fid, :fname, :fpath, :ftype, :fsize, :fhash, :course, :desc, 'processing', :uid, :t, :t)"""),
            {
                "fid": file_id, "fname": filename, "fpath": str(file_path),
                "ftype": file_type, "fsize": len(file_content), "fhash": file_hash,
                "course": course, "desc": description, "uid": uploaded_by, "t": now
            }
        )
        await db.commit()

    # 异步处理：提取文本 → 分块 → 向量化 → 入库
    try:
        text_content = extract_text(str(file_path), file_type)
        chunks = chunk_text(text_content, config.RAG_CHUNK_SIZE, config.RAG_CHUNK_OVERLAP)

        if not chunks:
            logger.warning("文件 {} 未提取到文本", filename)
            await _update_file_status(file_id, "failed", "未提取到文本内容")
            return {"file_id": file_id, "status": "failed", "message": "未提取到文本内容"}

        # Embedding + FAISS 入库
        vectors = embed_texts(chunks)
        start_index = add_vectors(vectors)

        # 写入分块表
        async with AsyncSessionLocal() as db:
            for i, chunk in enumerate(chunks):
                token_count = len(chunk) // 2  # 粗略估算
                await db.execute(
                    text("""INSERT INTO file_chunks
                            (file_id, chunk_index, content, token_count, char_count, faiss_index, created_at)
                            VALUES (:fid, :idx, :content, :tc, :cc, :fi, :t)"""),
                    {
                        "fid": file_id, "idx": i, "content": chunk,
                        "tc": token_count, "cc": len(chunk), "fi": start_index + i,
                        "t": now
                    }
                )
            await db.execute(
                text("UPDATE knowledge_files SET total_chunks = :tc, total_tokens = :tt, status = 'completed', updated_at = :t WHERE file_id = :fid"),
                {"tc": len(chunks), "tt": sum(len(c) // 2 for c in chunks), "t": now, "fid": file_id}
            )
            await db.commit()

        logger.info("文件处理完成: {} → {} 块", filename, len(chunks))
        return {"file_id": file_id, "status": "completed", "total_chunks": len(chunks), "filename": filename}

    except Exception as e:
        logger.error("文件处理失败: {} - {}", filename, e)
        await _update_file_status(file_id, "failed", str(e))
        return {"file_id": file_id, "status": "failed", "message": str(e)}


async def _update_file_status(file_id: str, status: str, error: str = None):
    async with AsyncSessionLocal() as db:
        await db.execute(
            text("UPDATE knowledge_files SET status = :s, error_message = :e WHERE file_id = :fid"),
            {"s": status, "e": error, "fid": file_id}
        )
        await db.commit()


async def get_file_status(file_id: str) -> dict:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("SELECT file_id, filename, status, total_chunks, error_message FROM knowledge_files WHERE file_id = :fid"),
            {"fid": file_id}
        )
        row = result.mappings().first()
        return dict(row) if row else None


async def get_file_detail(file_id: str) -> dict:
    """获取文件完整详情"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("""SELECT file_id, filename, file_type, file_size, file_hash, course,
                    description, total_chunks, total_tokens, status, error_message,
                    uploaded_by, created_at, updated_at
                    FROM knowledge_files WHERE file_id = :fid"""),
            {"fid": file_id}
        )
        row = result.mappings().first()
        if not row:
            return None

        detail = dict(row)

        # 获取分块数量
        chunk_result = await db.execute(
            text("SELECT COUNT(*) AS chunk_count FROM file_chunks WHERE file_id = :fid"),
            {"fid": file_id}
        )
        detail["chunk_count"] = chunk_result.scalar()
        return detail


async def list_files(course: str = None, page: int = 1, page_size: int = 20) -> dict:
    async with AsyncSessionLocal() as db:
        offset = (page - 1) * page_size
        where = "WHERE 1=1"
        params = {"limit": page_size, "offset": offset}
        if course:
            where += " AND course = :course"
            params["course"] = course

        result = await db.execute(text(f"""
            SELECT file_id, filename, file_type, file_size, course, description, total_chunks, status, created_at
            FROM knowledge_files {where}
            ORDER BY created_at DESC LIMIT :limit OFFSET :offset
        """), params)
        items = [dict(r) for r in result.mappings()]

        count_result = await db.execute(text(f"SELECT COUNT(*) AS c FROM knowledge_files {where}"), params)
        total = count_result.scalar()

        return {"list": items, "total": total, "page": page, "page_size": page_size}


async def delete_file(file_id: str) -> bool:
    """删除文件（同时清理 FAISS 向量和文件系统）"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("SELECT file_path FROM knowledge_files WHERE file_id = :fid"),
            {"fid": file_id}
        )
        row = result.mappings().first()
        if not row:
            return False

        # 删除文件系统
        try:
            Path(row["file_path"]).unlink(missing_ok=True)
        except Exception as e:
            logger.warning("删除文件失败: {}", e)

        # 删除数据库记录（file_chunks 会级联删除）
        await db.execute(text("DELETE FROM knowledge_files WHERE file_id = :fid"), {"fid": file_id})
        await db.commit()

        # 注意: FAISS 索引不直接删除单条向量（IndexFlatIP 不支持删除），需要重建
        logger.info("文件已删除: {}（注意: 需重建 FAISS 索引清理孤儿向量）", file_id)
        return True


async def rebuild_index() -> dict:
    """重建 FAISS 向量索引"""
    import faiss
    # 清空现有索引
    new_index = faiss.IndexFlatIP(config.EMBEDDING_DIM)
    faiss.write_index(new_index, config.FAISS_INDEX_PATH)

    # 重新加载所有已完成的分块
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            text("SELECT file_id, chunk_id, content FROM file_chunks ORDER BY file_id, chunk_index")
        )
        all_chunks = result.mappings().all()

    if not all_chunks:
        return {"total_files": 0, "total_chunks": 0}

    # 按文件分组
    files = set(r["file_id"] for r in all_chunks)
    texts = [r["content"] for r in all_chunks]
    vectors = embed_texts(texts)
    new_index.add(vectors)
    faiss.write_index(new_index, config.FAISS_INDEX_PATH)

    # 更新 faiss_index
    async with AsyncSessionLocal() as db:
        for i, row in enumerate(all_chunks):
            await db.execute(
                text("UPDATE file_chunks SET faiss_index = :idx WHERE chunk_id = :cid"),
                {"idx": i, "cid": row["chunk_id"]}
            )
        await db.commit()

    logger.info("FAISS 索引重建完成: {} 文件, {} 向量", len(files), len(all_chunks))
    return {"total_files": len(files), "total_chunks": len(all_chunks)}
