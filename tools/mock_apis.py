from langchain_core.tools import tool


@tool
def check_order_status(order_id: str) -> str:
    """当用户询问订单、物流状态、退换政策时使用此工具。必须传入订单号 order_id。"""
    print(f"  -> [Mock API] Querying database for order ID: {order_id}")
    
    # 丰富的模拟订单数据库，涵盖不同状态和场景
    mock_db = {
        # ========== 待发货 ==========
        "ORD-20260418-001": {
            "status": "待出库",
            "items": "Keychron K3 Pro × 1",
            "price": 699.00,
            "order_time": "2026-04-18 10:30",
            "message": "您的订单已确认，等待仓库打包。预计今天下午发货。"
        },
        
        # ========== 已发货 ==========
        "ORD-20260417-002": {
            "status": "运输中",
            "items": "雷蛇巴塞利斯蛇 V3 鼠标 × 1",
            "price": 349.00,
            "order_time": "2026-04-17 14:22",
            "tracking_number": "SF202604180001234",
            "courier": "顺丰速运",
            "location": "北京分拣中心",
            "estimated_delivery": "2026-04-19 18:00",
            "message": "您的订单已从北京分拣中心发出，顺丰速运，预计明日18:00前送达。当前位置：北京。"
        },
        
        "ORD-20260416-003": {
            "status": "运输中",
            "items": "索尼 WH-1000XM5 耳机 × 1",
            "price": 2699.00,
            "order_time": "2026-04-16 09:15",
            "tracking_number": "ZTO202604170005678",
            "courier": "中通快递",
            "location": "上海配送中心",
            "estimated_delivery": "2026-04-19 14:00",
            "courier_phone": "13812345678",
            "message": "您的订单已在上海配送中心，中通快递配送，预计4月19日送达。"
        },
        
        # ========== 已签收 ==========
        "ORD-20260414-004": {
            "status": "已签收",
            "items": "Suntory 乌龙茶 × 2 箱",
            "price": 158.00,
            "order_time": "2026-04-14 16:45",
            "delivery_time": "2026-04-16 10:30",
            "courier": "申通快递",
            "message": "您的订单已在2026-04-16 10:30签收，感谢您的购买！如有问题请在7天内提出售后申请。"
        },
        
        # ========== 退货中 ==========
        "ORD-20260410-005": {
            "status": "退货中",
            "items": "机械键盘 RGB 版本 × 1",
            "price": 799.00,
            "order_time": "2026-04-10 11:20",
            "return_reason": "按键失效，不符合预期",
            "return_tracking": "YTO202604160009999",
            "return_status": "已揽收，等待仓库检测",
            "message": "您的退货已揽收（单号：YTO202604160009999），目前在仓库检测中。预计3-5个工作日给出检测结果。通过后将原路退款至您的账户。"
        },
        
        # ========== 已退货 ==========
        "ORD-20260408-006": {
            "status": "已退货",
            "items": "蓝牙音箱 × 1",
            "price": 599.00,
            "order_time": "2026-04-08 13:50",
            "return_time": "2026-04-12 09:30",
            "refund_amount": 599.00,
            "refund_time": "2026-04-13 16:45",
            "message": "您的退货已完成，已于2026-04-13 16:45原路退款599.00元至您的付款账户，请在1-3个工作日内查收。"
        },
        
        # ========== 售后纠纷/需要人工处理 ==========
        "ORD-20260405-007": {
            "status": "售后处理中",
            "items": "智能手环 × 1",
            "price": 899.00,
            "order_time": "2026-04-05 15:30",
            "issue": "收到商品外观有划痕，要求更换",
            "service_level": "高优先级",
            "message": "您的售后申请已提交，评分：高优先级（需要更换）。我们的客服专员正在处理，预计2小时内联系您确认收货地址。"
        },
        
        "ORD-20260301-008": {
            "owner_id": "user456",
            "status": "异常",
            "items": "无线充电器 × 1",
            "price": 179.00,
            "order_time": "2026-03-01 10:00",
            "issue": "订单信息异常，查询无结果",
            "message": "抱歉，该订单号可能已过期（超过90天）或存在数据异常。请核实订单号，或直接联系人工客服（400-xxx-xxxx）处理历史订单。"
        }
    }
    
    # 查询逻辑：支持精确匹配或模糊查询
    if order_id in mock_db:
        order_info = mock_db[order_id]
        if order_info.get("owner_id", "user123") != "user123":
            return '{"auth_error": "Authentication Failed: This order does not belong to the current user."}'
        return order_info.get("message", "订单信息已返回")
    else:
        # 尝试模糊匹配（如果输入不是完整订单号）
        for oid, info in mock_db.items():
            if order_id.upper() in oid.upper():
                return info.get("message", "订单信息已返回")
        
        return f"未查到订单号 '{order_id}' 的信息。请确保订单号正确（格式如 ORD-20260418-001），或联系客服处理。"


# 辅助函数：获取完整订单详情（可用于日志/审计）
def get_order_details(order_id: str) -> dict:
    """内部函数，返回完整订单信息，不含敏感数据过滤"""
    mock_db = {
        "ORD-20260418-001": {
            "status": "待出库",
            "items": "Keychron K3 Pro × 1",
            "price": 699.00,
            "order_time": "2026-04-18 10:30",
            "message": "您的订单已确认，等待仓库打包。预计今天下午发货。"
        },
        "ORD-20260417-002": {
            "status": "运输中",
            "items": "雷蛇巴塞利斯蛇 V3 鼠标 × 1",
            "price": 349.00,
            "order_time": "2026-04-17 14:22",
            "tracking_number": "SF202604180001234",
            "courier": "顺丰速运",
            "location": "北京分拣中心",
            "estimated_delivery": "2026-04-19 18:00",
            "message": "您的订单已从北京分拣中心发出，顺丰速运，预计明日18:00前送达。当前位置：北京。"
        },
        "ORD-20260416-003": {
            "status": "运输中",
            "items": "索尼 WH-1000XM5 耳机 × 1",
            "price": 2699.00,
            "order_time": "2026-04-16 09:15",
            "tracking_number": "ZTO202604170005678",
            "courier": "中通快递",
            "location": "上海配送中心",
            "estimated_delivery": "2026-04-19 14:00",
            "courier_phone": "13812345678",
            "message": "您的订单已在上海配送中心，中通快递配送，预计4月19日送达。"
        },
        "ORD-20260414-004": {
            "status": "已签收",
            "items": "Suntory 乌龙茶 × 2 箱",
            "price": 158.00,
            "order_time": "2026-04-14 16:45",
            "delivery_time": "2026-04-16 10:30",
            "courier": "申通快递",
            "message": "您的订单已在2026-04-16 10:30签收，感谢您的购买！如有问题请在7天内提出售后申请。"
        },
        "ORD-20260410-005": {
            "status": "退货中",
            "items": "机械键盘 RGB 版本 × 1",
            "price": 799.00,
            "order_time": "2026-04-10 11:20",
            "return_reason": "按键失效，不符合预期",
            "return_tracking": "YTO202604160009999",
            "return_status": "已揽收，等待仓库检测",
            "message": "您的退货已揽收（单号：YTO202604160009999），目前在仓库检测中。预计3-5个工作日给出检测结果。通过后将原路退款至您的账户。"
        },
        "ORD-20260408-006": {
            "status": "已退货",
            "items": "蓝牙音箱 × 1",
            "price": 599.00,
            "order_time": "2026-04-08 13:50",
            "return_time": "2026-04-12 09:30",
            "refund_amount": 599.00,
            "refund_time": "2026-04-13 16:45",
            "message": "您的退货已完成，已于2026-04-13 16:45原路退款599.00元至您的付款账户，请在1-3个工作日内查收。"
        },
        "ORD-20260405-007": {
            "status": "售后处理中",
            "items": "智能手环 × 1",
            "price": 899.00,
            "order_time": "2026-04-05 15:30",
            "issue": "收到商品外观有划痕，要求更换",
            "service_level": "高优先级",
            "message": "您的售后申请已提交，评分：高优先级（需要更换）。我们的客服专员正在处理，预计2小时内联系您确认收货地址。"
        },
        "ORD-20260301-008": {
            "owner_id": "user456",
            "status": "异常",
            "items": "无线充电器 × 1",
            "price": 179.00,
            "order_time": "2026-03-01 10:00",
            "issue": "订单信息异常，查询无结果",
            "message": "抱歉，该订单号可能已过期（超过90天）或存在数据异常。请核实订单号，或直接联系人工客服（400-xxx-xxxx）处理历史订单。"
        }
    }
    order = mock_db.get(order_id, {})
    if not order:
        return {}
    if order.get("owner_id", "user123") != "user123":
        return {"auth_error": "Authentication Failed: This order does not belong to the current user."}
    return order