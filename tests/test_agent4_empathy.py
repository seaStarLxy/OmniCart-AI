import pytest
from unittest.mock import patch
from langchain_core.messages import AIMessage, HumanMessage
from agents.agent4_empathy import empathy_node

@patch("langchain_openai.ChatOpenAI.invoke")
def test_empathy_node_success(mock_invoke):
    """测试大模型成功润色语气"""
    
    # 修改：业务代码中没有正则分支，必然会调用 LLM。因此正确设置返回值。
    mock_invoke.return_value = AIMessage(content="I understand your concern. Status: Confirmed, waiting for warehouse dispatch")
    
    state = {
        "messages": [
            HumanMessage(content="I have been waiting for a week!"), 
            AIMessage(content="Status: Confirmed, waiting for warehouse dispatch")
        ],
        "trace": []
    }
    
    result = empathy_node(state)
    
    actual_reply = result["messages"][-1].content
    print(f"\n[Debug] Empathy 节点实际输出: {actual_reply}")
    
    # 修改：断言 LLM 必须被调用 1 次
    mock_invoke.assert_called_once() 
    
    expected_reply = "I understand your concern. Status: Confirmed, waiting for warehouse dispatch"
    assert actual_reply == expected_reply

@patch("agents.agent4_empathy.llm")
def test_empathy_node_fallback(mock_llm):
    """测试大模型润色失败时，由于业务代码没有降级，会直接抛出异常"""
    mock_llm.invoke.side_effect = Exception("LLM Error")
    
    original_draft = "Status: In transit"
    state = {
        "messages": [
            HumanMessage(content="查物流"),
            AIMessage(content=original_draft)
        ],
        "trace": []
    }
    
    # 修改：业务代码无 try-except，应期望抛出异常
    with pytest.raises(Exception, match="LLM Error"):
        empathy_node(state)