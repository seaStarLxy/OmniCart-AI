import pytest
from unittest.mock import patch
from langchain_core.messages import HumanMessage, AIMessage
from agents.agent1_router import triage_router_node

# 注意这里去掉了 .invoke，直接 mock 整个 llm 对象
@patch("agents.agent1_router.llm")
def test_router_node_to_agent3(mock_llm):
    """测试路由到 Agent 3 (订单处理)"""
    # 在 mock 对象上设置 invoke 的返回值
    mock_llm.invoke.return_value = AIMessage(content="Agent 3")
    
    state = {"messages": [HumanMessage(content="我的订单发货了吗？")], "trace": []}
    result = triage_router_node(state)
    
    assert "Agent 3" in result["next_agent"]
    assert "Router" in result["trace"][0]

@patch("agents.agent1_router.llm")
def test_router_node_to_agent2(mock_llm):
    """测试路由到 Agent 2 (导购)"""
    mock_llm.invoke.return_value = AIMessage(content="Agent 2")
    
    state = {"messages": [HumanMessage(content="推荐一款键盘")], "trace": []}
    result = triage_router_node(state)
    
    assert "Agent 2" in result["next_agent"]

@patch("agents.agent1_router.llm")
def test_router_node_fallback(mock_llm):
    """测试 LLM 挂掉时，系统是否能自动降级（默认路由到 Agent 2）"""
    mock_llm.invoke.side_effect = Exception("LLM Connection Error")
    
    state = {"messages": [HumanMessage(content="你好")], "trace": []}
    result = triage_router_node(state)
    
    assert "Agent 2" in result["next_agent"]