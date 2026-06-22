"""MySQL 异步连接池 — 使用 SQLAlchemy AsyncEngine"""
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
import config
from utils.logger import get_logger

logger = get_logger()

engine: AsyncEngine = create_async_engine(
    config.MYSQL_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    """FastAPI 依赖注入: 获取数据库会话"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def test_connection():
    """启动时测试数据库连接"""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("MySQL 连接成功: {}", config.MYSQL_DATABASE)
        return True
    except Exception as e:
        logger.error("MySQL 连接失败: {}", e)
        return False
