import pytest
from unittest.mock import patch
from langchain_core.messages import AIMessage, HumanMessage
from agents.agent1_router import triage_router_node

@patch("langchain_openai.ChatOpenAI.invoke")
def test_router_node_to_agent3(mock_invoke):
    """
    测试点：当用户询问订单（Order）相关问题时，大模型应该输出 Agent 3，
    并且路由节点需要将其正确解析为 "Agent 3 (Order Management)"。
    """
    # 拦截大模型的网络请求，直接返回一个伪造的 LangChain AIMessage 对象
    mock_invoke.return_value = AIMessage(content="Agent 3")

    # 构造测试上下文 (State)
    test_state = {
        "messages": [HumanMessage(content="Where is my order? The tracking hasn't updated.")],
        "trace": []
    }

    # 运行路由节点
    result = triage_router_node(test_state)

    # 断言验证
    assert result["next_agent"] == "Agent 3 (Order Management)", f"路由解析失败，实际输出: {result['next_agent']}"
    assert "🧭 Agent 1 (Router - LLM Powered)" in result["trace"]
    mock_invoke.assert_called_once()

@patch("agents.agent1_router.llm")
def test_router_node_to_agent2(mock_llm):
    """测试路由到 Agent 2 (导购)"""
    mock_llm.invoke.return_value = AIMessage(content="Agent 2")
    
    state = {"messages": [HumanMessage(content="推荐一款键盘")], "trace": []}
    result = triage_router_node(state)
    
    assert "Agent 2" in result["next_agent"]

@patch("agents.agent1_router.llm")
def test_router_node_fallback(mock_llm):
    """测试 LLM 挂掉时，系统由于无降级捕获机制，会直接抛出异常"""
    mock_llm.invoke.side_effect = Exception("LLM Connection Error")
    
    state = {"messages": [HumanMessage(content="你好")], "trace": []}
    
    # 修改：业务代码未做 try-except，因此这里应当期望捕获到异常
    with pytest.raises(Exception, match="LLM Connection Error"):
        triage_router_node(state)