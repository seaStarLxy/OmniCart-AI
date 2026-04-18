from langchain_core.tools import tool

@tool
def check_order_status(order_id: str) -> str:
    """当用户询问订单、物流状态时使用此工具。必须传入订单号 order_id。"""
    print(f"  -> [Mock API] 正在查询数据库，订单号: {order_id}")
    
    # 模拟内部数据库
    mock_db = {
        "12345": "您的订单已从北京发货，顺丰速运，预计明天送达。",
        "67890": "您的订单正在处理中，等待出库。"
    }
    
    return mock_db.get(order_id, "未查到该订单信息，请核对订单号是否正确。")