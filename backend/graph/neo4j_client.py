"""Neo4j 客户端 — 异步驱动连接池"""
from neo4j import AsyncGraphDatabase
import config
from utils.logger import get_logger

logger = get_logger()

_driver = None


async def get_driver():
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            config.NEO4J_URI,
            auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
        )
        try:
            await _driver.verify_connectivity()
            logger.info("Neo4j 连接成功: {}", config.NEO4J_URI)
        except Exception as e:
            logger.warning("Neo4j 连接失败(将在后续重试): {}", e)
    return _driver


async def close_driver():
    global _driver
    if _driver:
        await _driver.close()
        _driver = None
        logger.info("Neo4j 连接已关闭")


async def run_query(cypher: str, params: dict = None) -> list:
    """执行 Cypher 查询，返回记录列表"""
    driver = await get_driver()
    async with driver.session(database=config.NEO4J_DATABASE) as session:
        result = await session.run(cypher, params or {})
        records = await result.data()
        return records
