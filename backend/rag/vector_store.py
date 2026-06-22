"""FAISS 向量库管理 — 初始化、添加、搜索"""
import os
import numpy as np
import faiss
import config
from utils.logger import get_logger

logger = get_logger()

_index = None
_embedding_model = None


def get_embedding_model():
    """懒加载 Embedding 模型"""
    global _embedding_model
    if _embedding_model is None:
        from sentence_transformers import SentenceTransformer
        _embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
        logger.info("Embedding 模型加载完成: {}", config.EMBEDDING_MODEL)
    return _embedding_model


def get_index():
    """获取或创建 FAISS 索引"""
    global _index
    if _index is None:
        dim = config.EMBEDDING_DIM
        if os.path.exists(config.FAISS_INDEX_PATH):
            _index = faiss.read_index(config.FAISS_INDEX_PATH)
            logger.info("FAISS 索引加载完成: {} 条向量", _index.ntotal)
        else:
            _index = faiss.IndexFlatIP(dim)
            logger.info("FAISS 索引创建完成: dim={}", dim)
    return _index


def embed_texts(texts: list) -> np.ndarray:
    """文本列表 → 向量矩阵"""
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
    return embeddings.astype(np.float32)


def embed_query(text: str) -> np.ndarray:
    """单条文本 → 向量"""
    return embed_texts([text])


def add_vectors(vectors: np.ndarray) -> int:
    """向量入库，返回起始索引"""
    index = get_index()
    start = index.ntotal
    index.add(vectors)
    save_index()
    return start


def save_index():
    """持久化 FAISS 索引到磁盘"""
    if _index is not None:
        faiss.write_index(_index, config.FAISS_INDEX_PATH)


def search_vectors(query_vec: np.ndarray, top_k: int = 5):
    """向量检索，返回 (索引列表, 相似度列表)"""
    index = get_index()
    if index.ntotal == 0:
        return [], []
    scores, indices = index.search(query_vec, min(top_k, index.ntotal))
    return indices[0].tolist(), scores[0].tolist()


def get_index_info() -> dict:
    """获取索引信息"""
    index = get_index()
    return {
        "total_vectors": index.ntotal,
        "dimension": config.EMBEDDING_DIM,
        "embedding_model": config.EMBEDDING_MODEL,
        "index_type": "IndexFlatIP",
    }
