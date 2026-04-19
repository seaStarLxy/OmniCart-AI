from unittest.mock import patch

from langchain_core.messages import AIMessage, HumanMessage

from agents.agent4_empathy import empathy_node


# @patch("agents.agent4_empathy.llm")
# def test_empathy_node_success(mock_llm):
#     """测试大模型成功润色语气"""
#     mock_llm.invoke.return_value = AIMessage(content="非常理解您的焦急。您的订单预计明天送达。")
    
#     state = {
#         "messages": [
#             HumanMessage(content="我等了一周都没发货！"),
#             AIMessage(content="Status: Confirmed, waiting for warehouse dispatch")
#         ],
#         "trace": []
#     }
    
#     result = empathy_node(state)
    
#     assert result["messages"][-1].content == "非常理解您的焦急。您的订单预计明天送达。"
#     assert "❤️ Agent 4" in result["trace"][0]

def test_empathy_node_success():
    """测试正则成功润色语气 (waiting/anxious 分支)"""
    state = {
        "messages": [
            # 使用能触发第二条正则的英文，例如 "waiting"
            HumanMessage(content="I have been waiting for a week!"), 
            AIMessage(content="Status: Confirmed, waiting for warehouse dispatch")
        ],
        "trace": []
    }
    
    result = empathy_node(state)
    
    # 断言结果应该等于正则拼接后的字符串
    expected_reply = "I understand your concern. Status: Confirmed, waiting for warehouse dispatch"
    assert result["messages"][-1].content == expected_reply

@patch("agents.agent4_empathy.llm")
def test_empathy_node_fallback(mock_llm):
    """测试大模型润色失败时，保留原草稿回复"""
    mock_llm.invoke.side_effect = Exception("LLM Error")
    
    original_draft = "Status: In transit"
    state = {
        "messages": [
            HumanMessage(content="查物流"),
            AIMessage(content=original_draft)
        ],
        "trace": []
    }
    
    result = empathy_node(state)
    
    assert result["messages"][-1].content == original_draft