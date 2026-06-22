"""知识图谱服务层 — Cypher 查询封装"""
from graph.neo4j_client import run_query
from utils.logger import get_logger

logger = get_logger()


async def get_visualization_data(course: str = None, depth: int = 2, limit: int = 200) -> dict:
    """获取知识图谱可视化数据（节点+边）"""
    course_filter = ""
    params = {}
    if course:
        course_filter = "WHERE n.node_id STARTS WITH $prefix"
        params["prefix"] = course[:2]  # 'ml' or 'dm'

    nodes_data = await run_query(f"""
        MATCH (n) {course_filter}
        RETURN n.node_id AS id, n.name AS label, labels(n)[0] AS type, properties(n) AS props
        LIMIT {int(limit)}
    """, params)

    edges_data = await run_query(f"""
        MATCH (a)-[r]->(b)
        RETURN a.node_id AS source, b.node_id AS target, type(r) AS relation, properties(r) AS props
        LIMIT {int(limit)}
    """, {})

    categories = [
        {"name": "Course"}, {"name": "Chapter"},
        {"name": "KnowledgePoint"}, {"name": "Algorithm"}, {"name": "Application"}
    ]
    return {
        "nodes": nodes_data,
        "edges": edges_data,
        "categories": categories
    }


async def get_node_detail(node_id: str) -> dict:
    """查询知识点详情，含前置依赖、相似节点、关联算法"""
    node = await run_query(
        "MATCH (n {node_id: $id}) RETURN n.node_id AS node_id, n.name AS label, labels(n)[0] AS type, properties(n) AS props",
        {"id": node_id}
    )
    if not node:
        return None

    deps = await run_query(
        "MATCH (n {node_id: $id})-[:DEPENDS_ON]->(dep) RETURN dep.node_id AS node_id, dep.name AS label",
        {"id": node_id}
    )
    similar = await run_query(
        "MATCH (n {node_id: $id})-[r:SIMILAR_TO]->(s) RETURN s.node_id AS node_id, s.name AS label, r.similarity AS similarity, r.dimension AS dimension",
        {"id": node_id}
    )
    algos = await run_query(
        "MATCH (n {node_id: $id})-[:IMPLEMENTS]->(a:Algorithm) RETURN a.node_id AS node_id, a.name AS label, a.time_complexity AS complexity",
        {"id": node_id}
    )
    apps = await run_query(
        "MATCH (n {node_id: $id})-[:APPLIED_TO]->(app:Application) RETURN app.node_id AS node_id, app.name AS label, app.dataset AS dataset",
        {"id": node_id}
    )
    return {
        **node[0],
        "prerequisites": deps,
        "related_nodes": similar,
        "algorithms": algos,
        "applications": apps,
    }


async def search_nodes(keyword: str, course: str = None, limit: int = 10) -> list:
    """关键词搜索知识节点"""
    cypher = """
        MATCH (n) WHERE n.name CONTAINS $kw OR any(k IN COALESCE(n.keywords, []) WHERE k CONTAINS $kw)
    """
    params = {"kw": keyword}
    if course:
        cypher += " AND n.node_id STARTS WITH $prefix"
        params["prefix"] = course[:2]
    cypher += f" RETURN n.node_id AS node_id, n.name AS label, labels(n)[0] AS type, n.node_id AS course_ref LIMIT {int(limit)}"
    return await run_query(cypher, params)


async def get_learning_path(source: str, target: str) -> dict:
    """查询学习路径（最短路径）"""
    records = await run_query(f"""
        MATCH path = shortestPath(
          (start {{node_id: $src}})-[:DEPENDS_ON|CONTAINS*0..8]->(end {{node_id: $tgt}})
        )
        RETURN [node IN nodes(path) | node.node_id] AS path_ids,
               [node IN nodes(path) | node.name] AS path_labels,
               length(path) AS total_steps
    """, {"src": source, "tgt": target})
    if records:
        return records[0]
    return {"path": [], "path_labels": [], "total_steps": 0}


async def get_course_tree(course: str) -> dict:
    """获取课程知识树（树形结构）"""
    records = await run_query(
        "MATCH path = (c:Course)-[:CONTAINS*0..3]->(n) WHERE c.node_id STARTS WITH $prefix RETURN path",
        {"prefix": course[:2] if len(course) > 2 else course}
    )
    return {"course": course, "paths": records}


async def get_graph_stats() -> dict:
    """知识图谱统计信息"""
    total_nodes = await run_query("MATCH (n) RETURN count(n) AS cnt")
    total_edges = await run_query("MATCH ()-[r]->() RETURN count(r) AS cnt")
    by_type = await run_query("MATCH (n) RETURN labels(n)[0] AS type, count(n) AS cnt")
    by_relation = await run_query("MATCH ()-[r]->() RETURN type(r) AS relation, count(r) AS cnt")

    return {
        "total_nodes": total_nodes[0]["cnt"] if total_nodes else 0,
        "total_edges": total_edges[0]["cnt"] if total_edges else 0,
        "by_type": {r["type"]: r["cnt"] for r in by_type},
        "by_relation": {r["relation"]: r["cnt"] for r in by_relation},
    }


async def create_node(label: str, node_type: str, course: str = None, description: str = None,
                      difficulty: int = None, parent_id: str = None) -> dict:
    """创建知识节点"""
    node_id = f"{node_type[:3].lower()}_{label[:5].encode('utf-8').hex()[:8]}"
    props = {"node_id": node_id, "name": label, "description": description or ""}
    if difficulty:
        props["difficulty"] = difficulty
    if course:
        props["course"] = course

    type_label = node_type.capitalize() if node_type[0].islower() else node_type
    prop_str = ", ".join(f"{k}: ${k}" for k in props)
    await run_query(f"CREATE (n:{type_label} {{{prop_str}}})", props)

    if parent_id:
        await run_query(
            "MATCH (p {{node_id: $pid}}), (n {{node_id: $nid}}) CREATE (p)-[:CONTAINS]->(n)",
            {"pid": parent_id, "nid": node_id}
        )
    return {"node_id": node_id, "label": label, "type": node_type}


async def create_edge(source_id: str, target_id: str, relation: str, properties: dict = None) -> dict:
    """创建知识关系"""
    rel_type = relation.upper().replace(" ", "_")
    prop_str = ""
    params = {"src": source_id, "tgt": target_id}
    if properties:
        prop_str = " {" + ", ".join(f"{k}: ${k}" for k in properties) + "}"
        params.update(properties)
    await run_query(
        f"MATCH (a {{node_id: $src}}), (b {{node_id: $tgt}}) CREATE (a)-[:{rel_type}{prop_str}]->(b)",
        params
    )
    return {"source": source_id, "target": target_id, "relation": relation}


async def get_node_context_for_rag(keywords: list) -> dict:
    """RAG 增强: 从知识图谱提取上下文"""
    if not keywords:
        return {"related_nodes": [], "relations": []}

    nodes = []
    for kw in keywords[:5]:
        results = await run_query(
            "MATCH (n) WHERE n.name CONTAINS $kw RETURN n.node_id AS id, n.name AS name, n.description AS desc LIMIT 3",
            {"kw": kw}
        )
        for r in results:
            nodes.append(r)

    node_ids = [n["id"] for n in nodes]
    relations = []
    if node_ids:
        rel_data = await run_query(
            "MATCH (a)-[r]->(b) WHERE a.node_id IN $ids AND b.node_id IN $ids RETURN a.name AS source, type(r) AS rel, b.name AS target",
            {"ids": node_ids}
        )
        relations = [f"{r['source']} {r['rel']} {r['target']}" for r in rel_data]

    return {"related_nodes": [n["name"] for n in nodes], "relations": relations}
