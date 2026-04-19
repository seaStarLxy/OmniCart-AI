import pytest
from langchain_core.messages import HumanMessage
from agents.agent3_order import _translate_text, _format_order_reply, order_node
from unittest.mock import patch

def test_translate_text():
    """测试文本中英替换逻辑"""
    text = "商品：雷蛇巴塞利斯蛇 V3 鼠标，状态：高优先级"
    result = _translate_text(text)
    assert "Razer Basilisk V3 mouse" in result
    assert "High priority" in result

def test_format_order_reply_valid():
    """测试正常订单信息的格式化拼接"""
    mock_info = {
        "status": "运输中",
        "items": "蓝牙音箱 × 1",
        "price": 599.00,
        "order_time": "2026-04-18",
        "tracking_number": "SF123456"
    }
    result = _format_order_reply("ORD-123", mock_info)
    assert "In transit" in result
    assert "Bluetooth speaker" in result
    assert "RMB 599.00" in result
    assert "SF123456" in result

def test_format_order_reply_invalid():
    """测试查不到订单时的回复"""
    result = _format_order_reply("ORD-999", {})
    assert "could not find order ORD-999" in result

@patch("agents.agent3_order.get_order_details")
def test_order_node_with_valid_id(mock_get_details):
    """测试提取到订单号的流程"""
    mock_get_details.return_value = {"status": "已签收", "items": "Suntory 乌龙茶"}
    
    state = {"messages": [HumanMessage(content="帮我查查 ORD-20260417-002")], "trace": []}
    result = order_node(state)
    
    reply_text = result["messages"][-1].content
    assert "Delivered" in reply_text
    assert "Suntory oolong tea" in reply_text
    assert "Agent 3" in result["trace"][0]

def test_order_node_missing_id():
    """测试未提取到订单号时，反问用户提供 ID 的流程"""
    state = {"messages": [HumanMessage(content="帮我查查我的快递到哪了")], "trace": []}
    result = order_node(state)
    
    reply_text = result["messages"][-1].content
    assert "Please provide the order ID" in reply_text
