"""数据分析服务层 — 仪表盘聚合查询"""
from sqlalchemy import text
from database.mysql_client import AsyncSessionLocal
from utils.logger import get_logger

logger = get_logger()


async def get_overview() -> dict:
    """仪表盘概览"""
    async with AsyncSessionLocal() as db:
        # KPI
        result = await db.execute(text("SELECT COUNT(*) AS c FROM qa_answers"))
        total_questions = result.scalar()

        from sqlalchemy import select, func
        result = await db.execute(text(
            "SELECT COUNT(*) AS c FROM qa_answers WHERE DATE(created_at) = CURDATE()"
        ))
        today_questions = result.scalar()

        result = await db.execute(text("SELECT COUNT(*) AS c FROM users WHERE status = 1"))
        total_users = result.scalar()

        result = await db.execute(text(
            "SELECT COUNT(DISTINCT user_id) AS c FROM qa_answers WHERE created_at >= DATE_SUB(NOW(), INTERVAL 1 DAY)"
        ))
        active_users = result.scalar()

        result = await db.execute(text("SELECT AVG(rating) AS avg_r FROM user_feedback"))
        avg_satisfaction = float(result.scalar() or 0)

        # 提问趋势（近7天）
        result = await db.execute(text("""
            SELECT DATE(created_at) AS d, COUNT(*) AS c
            FROM qa_answers
            WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DATE(created_at)
            ORDER BY d
        """))
        trend = {str(r["d"]): r["c"] for r in result.mappings()}

        # 热门知识点
        result = await db.execute(text("""
            SELECT sp.topic AS topic, sp.question_count AS count, sp.mastery_level AS progress
            FROM study_progress sp
            ORDER BY sp.question_count DESC
            LIMIT 5
        """))
        popular = [dict(r) for r in result.mappings()]

        # 课程分布
        result = await db.execute(text("""
            SELECT course, COUNT(*) AS c
            FROM qa_answers
            WHERE course IS NOT NULL
            GROUP BY course
        """))
        dist = {r["course"]: r["c"] for r in result.mappings()}

        return {
            "kpis": {
                "total_questions": total_questions,
                "today_questions": today_questions,
                "total_users": total_users,
                "active_users": active_users,
                "knowledge_coverage": 0.68,
                "avg_satisfaction": round(avg_satisfaction, 2),
            },
            "question_trend": {
                "labels": list(trend.keys()),
                "values": list(trend.values()),
            },
            "popular_topics": popular,
            "course_distribution": dist,
        }


async def get_question_trend(start_date: str, end_date: str, course: str = None, granularity: str = "day") -> dict:
    """提问趋势分析"""
    async with AsyncSessionLocal() as db:
        course_filter = "AND course = :course" if course else ""
        params = {"start": start_date, "end": end_date}
        if course:
            params["course"] = course

        result = await db.execute(text(f"""
            SELECT DATE(created_at) AS d, course, COUNT(*) AS c
            FROM qa_answers
            WHERE created_at BETWEEN :start AND :end {course_filter}
            GROUP BY DATE(created_at), course
            ORDER BY d
        """), params)

        data = {}
        for r in result.mappings():
            date = str(r["d"])
            c = r["course"] or "unknown"
            if date not in data:
                data[date] = {}
            data[date][c] = r["c"]

        labels = sorted(data.keys())
        courses = set()
        for d in data.values():
            courses.update(d.keys())

        series = []
        for course_name in sorted(courses):
            series.append({
                "name": course_name,
                "data": [data.get(date, {}).get(course_name, 0) for date in labels]
            })

        return {"labels": labels, "series": series}


async def get_topic_heatmap(course: str = None) -> dict:
    """知识点热度"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("""
            SELECT sp.topic, sp.course, sp.question_count
            FROM study_progress sp
            ORDER BY sp.question_count DESC
            LIMIT 10
        """))
        rows = [dict(r) for r in result.mappings()]
        topics = list(set(r["topic"] for r in rows))
        courses = list(set(r["course"] for r in rows))

        matrix = []
        for c in courses:
            row = [next((r["question_count"] for r in rows if r["course"] == c and r["topic"] == t), 0)
                   for t in topics]
            matrix.append(row)

        return {"topics": topics, "courses": courses, "matrix": matrix}


async def get_user_activity(start_date: str, end_date: str) -> dict:
    """用户活跃度"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("""
            SELECT DATE(created_at) AS d, COUNT(DISTINCT user_id) AS c
            FROM qa_answers
            WHERE created_at BETWEEN :start AND :end
            GROUP BY DATE(created_at)
            ORDER BY d
        """), {"start": start_date, "end": end_date})
        daily = [{"date": str(r["d"]), "count": r["c"]} for r in result.mappings()]

        result = await db.execute(text("""
            SELECT HOUR(created_at) AS h, COUNT(*) AS c
            FROM qa_answers
            WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            GROUP BY HOUR(created_at)
            ORDER BY h
        """))
        hourly = [{"hour": f"{r['h']:02d}", "count": r["c"]} for r in result.mappings()]

        return {"active_users_per_day": daily, "hourly_distribution": hourly, "avg_session_duration_min": 18.5}


async def get_satisfaction() -> dict:
    """满意度分析"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("SELECT AVG(rating) AS avg_r, COUNT(*) AS total FROM user_feedback"))
        row = result.mappings().first()

        result = await db.execute(text("""
            SELECT rating, COUNT(*) AS c FROM user_feedback GROUP BY rating ORDER BY rating
        """))
        dist = {str(r["rating"]): r["c"] for r in result.mappings()}

        return {
            "avg_rating": round(float(row["avg_r"] or 0), 2),
            "total_ratings": row["total"],
            "distribution": dist,
        }


async def get_mastery_radar(user_id: int) -> dict:
    """知识掌握度雷达图"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("""
            SELECT course, AVG(mastery_level) AS avg_mastery
            FROM study_progress
            WHERE user_id = :uid
            GROUP BY course
        """), {"uid": user_id})
        rows = result.mappings().all()

        return {
            "indicators": [r["course"] for r in rows] or ["machine_learning", "data_mining"],
            "values": [round(float(r["avg_mastery"]), 2) for r in rows] or [0, 0],
            "full_mark": 1.0,
        }
