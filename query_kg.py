# -*- coding: utf-8 -*-
"""
知识图谱查询与验证脚本
======================
在构建完知识图谱后运行此脚本，验证数据完整性并体验常用查询。

使用方法：
  python query_kg.py

也可在 Neo4j Browser (http://localhost:7474) 中直接运行下面的 Cypher 语句。
"""

from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"  # ← 改成你设的密码


def print_section(title):
    print(f"\n{'=' * 50}")
    print(f"  {title}")
    print(f"{'=' * 50}")


def run_query(tx, cypher, title=None):
    """运行查询并打印结果"""
    if title:
        print(f"\n--- {title} ---")
    result = tx.run(cypher)
    records = list(result)
    for r in records:
        print(f"  {dict(r)}")
    return records


def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    driver.verify_connectivity()

    with driver.session() as session:

        # ===================== 统计验证 =====================
        print_section("图谱统计")

        session.execute_read(
            run_query,
            "MATCH (n:MLNode) RETURN labels(n) AS labels, count(n) AS cnt ORDER BY cnt DESC",
            "各标签节点数"
        )

        session.execute_read(
            run_query,
            "MATCH ()-[r]->() RETURN type(r) AS rel, count(r) AS cnt ORDER BY cnt DESC",
            "各关系类型数量"
        )

        session.execute_read(
            run_query,
            """
            MATCH (n:MLNode)
            RETURN n.id AS id, n.name AS name, labels(n) AS labels
            WHERE NOT ()-->(n) AND NOT (n)-->()
            LIMIT 10
            """,
            "孤立节点检查（应返回空）"
        )

        # ===================== 知识路径查询 =====================
        print_section("知识路径查询")

        session.execute_read(
            run_query,
            """
            MATCH path = (start:MLNode {id: 'c_ml'})-[:PARADIGM|BELONGS_TO|EXTENDS*1..4]->(end:Algorithm)
            RETURN end.name AS algorithm, length(path) AS depth
            ORDER BY depth
            LIMIT 20
            """,
            "从「机器学习」出发，探索所有可达算法"
        )

        session.execute_read(
            run_query,
            """
            MATCH (a:Algorithm {id: 'a_transformer'})
            OPTIONAL MATCH (a)-[:BASED_ON]->(base:MLNode)
            OPTIONAL MATCH (a)-[:USES]->(tech:Technique)
            OPTIONAL MATCH (a)-[:APPLIES_TO]->(app:Application)
            RETURN
              a.name AS model,
              collect(DISTINCT base.name) AS based_on,
              collect(DISTINCT tech.name) AS techniques,
              collect(DISTINCT app.name) AS applications
            """,
            "Transformer 全景信息"
        )

        session.execute_read(
            run_query,
            """
            MATCH (ch:Chapter)-[:CONTAINS]->(c:Concept)<-[:BELONGS_TO]-(a:Algorithm)
            WITH ch, count(a) AS algo_cnt
            MATCH (ch)-[:CONTAINS]->(c2:Concept)<-[:USES]-(t:Technique)
            RETURN ch.name AS chapter, algo_cnt, count(DISTINCT t) AS tech_cnt
            ORDER BY algo_cnt DESC
            """,
            "各章节的算法数与技术数"
        )

        # ===================== 学习路径推荐 =====================
        print_section("学习路径推荐")

        session.execute_read(
            run_query,
            """
            MATCH (a:Algorithm {id: 'a_xgboost'})-[:BELONGS_TO]->(c:Concept)<-[:CONTAINS]-(ch:Chapter)
            MATCH (ch)-[:HAS_PREREQ*0..5]->(pre:Chapter)
            WITH DISTINCT pre
            MATCH (pre)-[:CONTAINS]->(pc:Concept)
            RETURN pre.name AS chapter, collect(pc.name)[0..5] AS key_concepts
            ORDER BY pre.id
            """,
            "学习 XGBoost 的前置知识链"
        )

        session.execute_read(
            run_query,
            """
            MATCH (a:Algorithm {id: 'a_bert'})-[:BELONGS_TO]->(c:Concept)<-[:CONTAINS]-(ch:Chapter)
            MATCH (ch)-[:HAS_PREREQ*0..5]->(pre:Chapter)
            WITH DISTINCT pre
            MATCH (pre)-[:CONTAINS]->(pc:Concept)
            RETURN pre.name AS chapter, collect(pc.name)[0..5] AS key_concepts
            ORDER BY pre.id
            """,
            "学习 BERT 的前置知识链"
        )

        # ===================== 相似度分析 =====================
        print_section("算法关联分析")

        session.execute_read(
            run_query,
            """
            MATCH (a1:Algorithm)-[:USES]->(t:Technique)<-[:USES]-(a2:Algorithm)
            WHERE a1.id < a2.id
            WITH a1, a2, count(t) AS shared
            WHERE shared >= 3
            RETURN a1.name AS algo1, a2.name AS algo2, shared
            ORDER BY shared DESC
            LIMIT 15
            """,
            "共享技术最多的算法对"
        )

        session.execute_read(
            run_query,
            """
            MATCH (a:Algorithm)-[:APPLIES_TO]->(app:Application)
            WITH app, collect(a.name) AS algos, count(a) AS cnt
            WHERE cnt >= 3
            RETURN app.name AS application, algos, cnt
            ORDER BY cnt DESC
            """,
            "算法最密集的应用领域"
        )

        # ===================== 推荐可视化查询 =====================
        print_section("Neo4j Browser 推荐查询（复制到浏览器运行）")
        print("""
  1. 全局概览（前200节点）:
     MATCH (n:MLNode) RETURN n LIMIT 200

  2. 某章节知识子图:
     MATCH (ch:Chapter {name: '深度学习'})-[:CONTAINS]->(c)
     OPTIONAL MATCH (c)<-[:BELONGS_TO]-(a:Algorithm)
     OPTIONAL MATCH (a)-[:USES]->(t:Technique)
     RETURN ch, c, a, t

  3. 学习路径图:
     MATCH path = (ch1:Chapter)-[:HAS_PREREQ*1..3]->(ch2:Chapter)
     RETURN path

  4. 技术依赖网络:
     MATCH (a:Algorithm)-[:USES]->(t:Technique)
     WHERE t.category = '优化'
     RETURN a, t

  5. 应用领域分布:
     MATCH (a:Algorithm)-[:APPLIES_TO]->(app:Application)
     RETURN app, collect(a.name) AS algorithms

  6. 最短路径查询:
     MATCH path = shortestPath(
       (a:MLNode {name: '线性回归'})-[*..10]-(b:MLNode {name: 'Transformer'})
     )
     RETURN path
""")

    driver.close()
    print("\n查询完成!")


if __name__ == "__main__":
    main()
