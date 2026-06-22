"""知识图谱路由 — /api/v1/graph"""
from fastapi import APIRouter, Depends, Query
from api.deps import get_current_user, require_role
from models.schemas import UserOut, NodeCreate, EdgeCreate
from service import graph_service
from utils.response import success, error

router = APIRouter()


@router.get("/visualization")
async def visualization(course: str = Query(default=None), depth: int = Query(default=2), limit: int = Query(default=200)):
    try:
        data = await graph_service.get_visualization_data(course, depth, limit)
        return success(data)
    except Exception as e:
        return error(500, f"获取图谱数据失败: {e}")


@router.get("/node/{node_id}")
async def node_detail(node_id: str):
    try:
        data = await graph_service.get_node_detail(node_id)
        if not data:
            return error(404, "节点不存在")
        return success(data)
    except Exception as e:
        return error(500, f"查询节点失败: {e}")


@router.get("/search")
async def search(keyword: str = Query(...), course: str = Query(default=None), limit: int = Query(default=10)):
    try:
        data = await graph_service.search_nodes(keyword, course, limit)
        return success(data)
    except Exception as e:
        return error(500, f"搜索失败: {e}")


@router.get("/path")
async def learning_path(source: str = Query(...), target: str = Query(...)):
    try:
        data = await graph_service.get_learning_path(source, target)
        return success(data)
    except Exception as e:
        return error(500, f"路径查询失败: {e}")


@router.get("/tree/{course}")
async def course_tree(course: str):
    try:
        data = await graph_service.get_course_tree(course)
        return success(data)
    except Exception as e:
        return error(500, f"获取知识树失败: {e}")


@router.get("/stats")
async def stats():
    try:
        data = await graph_service.get_graph_stats()
        return success(data)
    except Exception as e:
        return error(500, f"获取统计失败: {e}")


@router.post("/nodes")
async def create_node(req: NodeCreate, user: UserOut = Depends(require_role("teacher", "admin"))):
    try:
        data = await graph_service.create_node(req.label, req.type, req.course, req.description, req.difficulty, req.parent_id)
        return success(data, "节点创建成功")
    except Exception as e:
        return error(500, f"创建节点失败: {e}")


@router.post("/edges")
async def create_edge(req: EdgeCreate, user: UserOut = Depends(require_role("teacher", "admin"))):
    try:
        data = await graph_service.create_edge(req.source_id, req.target_id, req.relation, req.properties)
        return success(data, "关系创建成功")
    except Exception as e:
        return error(500, f"创建关系失败: {e}")
