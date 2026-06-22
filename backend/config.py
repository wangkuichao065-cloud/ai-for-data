"""后端配置文件 — 集中管理所有配置项"""
import os
from pathlib import Path

# ============================================================
# 路径配置
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOAD_DIR = DATA_DIR / "uploads"
FAISS_DIR = DATA_DIR / "faiss_index"
STATIC_DIR = BASE_DIR / "static"
LOG_DIR = BASE_DIR / "logs"

for d in [DATA_DIR, UPLOAD_DIR, FAISS_DIR, STATIC_DIR, LOG_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ============================================================
# MySQL 配置 (用户: root / 密码: root / 数据库: ai_for_data)
# ============================================================
MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"
MYSQL_DATABASE = "ai_for_data"

MYSQL_URL = f"mysql+aiomysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"

# ============================================================
# Neo4j 配置
# ============================================================
NEO4J_URI = "bolt://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "neo4j"
NEO4J_DATABASE = "knowledge_graph"

# ============================================================
# FAISS / Embedding 配置
# ============================================================
FAISS_INDEX_PATH = str(FAISS_DIR / "index.faiss")
EMBEDDING_MODEL = "BAAI/bge-small-zh-v1.5"
EMBEDDING_DIM = 512
RAG_CHUNK_SIZE = 500
RAG_CHUNK_OVERLAP = 50
RAG_TOP_K = 5
RAG_SIMILARITY_THRESHOLD = 0.5

# ============================================================
# Ollama / DeepSeek 配置
# ============================================================
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = "deepseek-r1:7b"
LLM_TEMPERATURE = 0.7
LLM_MAX_TOKENS = 2048
LLM_CONTEXT_WINDOW = 4096

# ============================================================
# IndexTTS2 配置
# ============================================================
INDEXTTS_CHECKPOINTS = str(BASE_DIR / "checkpoints")
INDEXTTS_CFG = str(Path(INDEXTTS_CHECKPOINTS) / "config.yaml")
INDEXTTS_VOICE_PROMPT = str(STATIC_DIR / "voice_prompt.wav")  # 默认音色参考音频
INDEXTTS_USE_FP16 = True  # 8GB显存建议开启
INDEXTTS_USE_CUDA = True

# ============================================================
# Stable Diffusion 配置
# ============================================================
SD_MODEL_PATH = "runwayml/stable-diffusion-v1-5"
SD_DEVICE = "cuda"
SD_DEFAULT_STEPS = 20
SD_DEFAULT_CFG = 7.5

# ============================================================
# GPU 策略 (8GB 显存交替加载)
# ============================================================
GPU_TOTAL_MEMORY_GB = 8
GPU_STRATEGY = "alternate"  # alternate / exclusive

# ============================================================
# JWT 认证
# ============================================================
JWT_SECRET = "change-me-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 2
JWT_REFRESH_EXPIRE_HOURS = 168  # 7天

# ============================================================
# CORS
# ============================================================
CORS_ORIGINS = [
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "null",  # 本地 file:// 打开的 HTML
    "*",
]

# ============================================================
# 应用信息
# ============================================================
APP_TITLE = "课程知识图谱与智能问答平台"
APP_VERSION = "1.0.0"
