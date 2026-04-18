import re
from core.state import AgentState

def triage_router_node(state: AgentState) -> dict:
    user_input = state["messages"][-1]
    print(f"\n[Agent 1 - Router] 正在利用大模型分析输入: {user_input}")

    normalized_input = str(getattr(user_input, "content", user_input)).lower()
    has_order_id = bool(re.search(r"ord-\d{8}-\d{3}", normalized_input, re.IGNORECASE))
    order_keywords = [
        "订单", "退款", "退货", "物流", "发货", "快递", "售后",
        "order", "refund", "return", "shipping", "delivery", "track", "tracking", "after-sales"
    ]

    if has_order_id or any(keyword in normalized_input for keyword in order_keywords):
        decision = "Agent 3 (Order Management)"
    else:
        decision = "Agent 2 (Sales & RAG)"

    print(f"[Agent 1 - Router] 决定路由至: {decision}")
    trace = state.get("trace", []) + ["🧭 Agent 1 (Router)"]
    return {"next_agent": decision, "trace": trace}