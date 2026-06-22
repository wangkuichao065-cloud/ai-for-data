"""文档处理 — PDF/TXT/DOCX → 文本 → 分块"""
import os
import re
from typing import Optional
from utils.logger import get_logger
import config

logger = get_logger()


def extract_text(file_path: str, file_type: str) -> str:
    """从文件中提取纯文本"""
    if file_type == "txt" or file_type == "md":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    if file_type == "pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            return "\n\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            logger.error("PDF 解析失败: {}", e)
            return ""

    if file_type == "docx":
        try:
            from docx import Document
            doc = Document(file_path)
            return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            logger.error("DOCX 解析失败: {}", e)
            return ""

    logger.warning("不支持的文件类型: {}", file_type)
    return ""


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> list:
    """文本分块 — 按字符数切分，带重叠"""
    chunk_size = chunk_size or config.RAG_CHUNK_SIZE
    overlap = overlap or config.RAG_CHUNK_OVERLAP

    if not text.strip():
        return []

    # 清理多余空白
    text = re.sub(r"\s+", " ", text).strip()

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # 尝试在句号处断句，避免截断句子
        if end < len(text):
            last_period = chunk.rfind("。")
            if last_period > chunk_size * 0.5:
                end = start + last_period + 1
                chunk = text[start:end]

        chunks.append(chunk.strip())
        start = end - overlap

    logger.info("文本分块完成: {} 字符 → {} 块", len(text), len(chunks))
    return chunks


def get_file_type(filename: str) -> str:
    """从文件名提取类型"""
    ext = os.path.splitext(filename)[1].lower().lstrip(".")
    if ext in ("pdf", "txt", "docx", "md"):
        return ext
    return "unknown"
