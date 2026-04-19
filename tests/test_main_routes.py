from main import check_safety, route_decision


def test_check_safety():
    """测试安防网关的条件路由"""
    # 1. 安全请求进入主业务
    assert check_safety({"is_safe": True}) == "router"
    
    # 2. 不安全请求直接去日志
    assert check_safety({"is_safe": False}) == "logger"

def test_route_decision():
    """测试业务网关的条件路由"""
    # 1. 明确是 Agent 3
    assert route_decision({"next_agent": "Agent 3 (Order Management)"}) == "order_agent"
    
    # 2. 否则默认走 RAG (Agent 2)
    assert route_decision({"next_agent": "Agent 2 (Sales & RAG)"}) == "rag_agent"
    assert route_decision({"next_agent": "随便什么其他字符"}) == "rag_agent"
