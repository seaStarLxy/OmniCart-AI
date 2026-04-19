import re

from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

from core.config import settings
from core.state import AgentState
from tools.mock_apis import get_order_details

llm = ChatOpenAI(
    model=settings.active_model,
    api_key=settings.active_api_key,
    base_url=settings.active_base_url,
    temperature=0.1,
    max_tokens=512,
)

@tool
def _get_order_tool(order_id: str) -> dict:
    """
    Fetch comprehensive details for a specific order.
    Returns tracking info, items, status, and shipping details.
    Argument MUST be a valid order ID format: e.g. ORD-20260418-001
    """
    print(f"  -> [Agent 3 Tool Call] Executing _get_order_tool with order_id: {order_id}")
    return get_order_details(order_id)

STATUS_MAP = {
    "待出库": "Confirmed, waiting for warehouse dispatch",
    "运输中": "In transit",
    "已签收": "Delivered",
    "退货中": "Return in progress",
    "已退货": "Returned",
    "售后处理中": "After-sales service in progress",
    "异常": "Exception"
}

TEXT_REPLACEMENTS = {
    "雷蛇巴塞利斯蛇 V3 鼠标": "Razer Basilisk V3 mouse",
    "索尼 WH-1000XM5 耳机": "Sony WH-1000XM5 headphones",
    "机械键盘 RGB 版本": "RGB mechanical keyboard",
    "蓝牙音箱": "Bluetooth speaker",
    "智能手环": "Smart band",
    "无线充电器": "Wireless charger",
    "Suntory 乌龙茶": "Suntory oolong tea",
    "顺丰速运": "SF Express",
    "中通快递": "ZTO Express",
    "申通快递": "STO Express",
    "北京分拣中心": "Beijing sorting center",
    "上海配送中心": "Shanghai distribution center",
    "已揽收，等待仓库检测": "Collected and waiting for warehouse inspection",
    "收到商品外观有划痕，要求更换": "Customer reported cosmetic scratches and requested a replacement",
    "高优先级": "High priority",
    "订单信息异常，查询无结果": "Order record is abnormal and no normal lookup result is available"
}


def _translate_text(text: str) -> str:
    if not text:
        return text
    translated = text
    for source, target in TEXT_REPLACEMENTS.items():
        translated = translated.replace(source, target)
    return translated


def _format_order_reply(order_id: str, order_info: dict) -> str:
    if not order_info:
        return f"I could not find order {order_id}. Please verify the order ID format, for example: ORD-20260418-001."

    status = STATUS_MAP.get(order_info.get("status", "Unknown"), order_info.get("status", "Unknown"))
    items = _translate_text(order_info.get("items", "Unknown item"))
    price = order_info.get("price")
    order_time = order_info.get("order_time", "Unknown")

    lines = [
        f"Here is the latest update for order {order_id}.",
        f"Status: {status}.",
        f"Items: {items}.",
    ]
    if price is not None:
        lines.append(f"Order amount: RMB {price:.2f}.")
    lines.append(f"Order time: {order_time}.")

    if order_info.get("courier"):
        lines.append(f"Courier: {_translate_text(order_info['courier'])}.")
    if order_info.get("tracking_number"):
        lines.append(f"Tracking number: {order_info['tracking_number']}.")
    if order_info.get("location"):
        lines.append(f"Current location: {_translate_text(order_info['location'])}.")
    if order_info.get("estimated_delivery"):
        lines.append(f"Estimated delivery: {order_info['estimated_delivery']}.")
    if order_info.get("courier_phone"):
        lines.append(f"Courier phone: {order_info['courier_phone']}.")
    if order_info.get("delivery_time"):
        lines.append(f"Delivered at: {order_info['delivery_time']}.")
    if order_info.get("return_status"):
        lines.append(f"Return status: {_translate_text(order_info['return_status'])}.")
    if order_info.get("return_tracking"):
        lines.append(f"Return tracking number: {order_info['return_tracking']}.")
    if order_info.get("refund_amount") is not None:
        lines.append(f"Refund amount: RMB {order_info['refund_amount']:.2f}.")
    if order_info.get("refund_time"):
        lines.append(f"Refund completed at: {order_info['refund_time']}.")
    if order_info.get("issue"):
        lines.append(f"Issue noted: {_translate_text(order_info['issue'])}.")
    if order_info.get("service_level"):
        lines.append(f"Service level: {_translate_text(order_info['service_level'])}.")

    return "\n".join(lines)

def order_node(state: AgentState):
    print("\n[Agent 3 - Order Management] 接管对话，启动 ReAct 规划与工具调用循环...")
    messages = state.get("messages", [])
    
    # ==========================================
    # ReAct Step 1: THINK — 从用户消息中提取订单号
    # ==========================================
    user_text = ""
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "human":
            user_text = msg.content
            break
        elif hasattr(msg, "content"):
            user_text = msg.content
            break
    
    order_match = re.search(r'(ORD-\d{8}-\d{3})', str(user_text), re.IGNORECASE)
    
    if not order_match:
        # ReAct 推理结论：缺少参数，无法调用工具，直接回复
        print("  -> [Agent 3 思考] 用户未提供订单号，无法调用工具，要求用户补充信息。")
        fallback = AIMessage(content="I can help with that. Please provide the order ID, for example: ORD-20260417-002.")
        trace = state.get("trace", []) + ["📦 Agent 3 (ReAct - Need More Info)"]
        return {"messages": messages + [fallback], "trace": trace}
    
    order_id = order_match.group(1).upper()
    print(f"  -> [Agent 3 思考] 识别到订单号 {order_id}，我需要调用工具获取订单详情。")
    
    # ==========================================
    # ReAct Step 2: ACT — 调用工具获取事实数据
    # ==========================================
    print(f"  -> [Agent 3 工具调用] Executing _get_order_tool(order_id='{order_id}')")
    tool_result = get_order_details(order_id)
    context_data = str(tool_result)
    print(f"  -> [Agent 3 观察] 工具返回数据: {context_data}")
    
    # ==========================================
    # ReAct Step 3: OBSERVE & RESPOND — 根据事实数据生成结构化回复
    # ==========================================
    reply = _format_order_reply(order_id, tool_result)
    print("  -> [Agent 3 结论] 基于工具返回的事实数据，生成最终结构化回复。")
    
    final_output = AIMessage(content=reply)
    trace = state.get("trace", []) + ["📦 Agent 3 (Order - ReAct Loop)"]
    return {
        "messages": messages + [final_output], 
        "trace": trace,
        "context": context_data  # 传递给 Agent 5 做事实核查
    }