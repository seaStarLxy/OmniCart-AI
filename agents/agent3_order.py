import re
from langchain_core.messages import AIMessage
from core.state import AgentState
from tools.mock_apis import get_order_details


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
    print("\n[Agent 3 - Order Management] 接管对话，思考中...")
    messages = state.get("messages", [])
    
    match = None
    for msg in reversed(messages):
        msg_text = msg.content if hasattr(msg, 'content') else str(msg)
        match = re.search(r"ORD-\d{8}-\d{3}", msg_text, re.IGNORECASE)
        if match:
            break

    if not match:
        trace = state.get("trace", []) + ["📦 Agent 3 (Order)"]
    return {"messages": messages + [AIMessage(content="I can help with that. Please provide the order ID, for example: ORD-20260417-002.")], "trace": trace}

    order_id = match.group(0).upper()
    order_info = get_order_details(order_id)
    reply = _format_order_reply(order_id, order_info)
    trace = state.get("trace", []) + ["📦 Agent 3 (Order)"]
    return {"messages": messages + [AIMessage(content=reply)], "trace": trace}