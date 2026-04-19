import json
from langchain_core.messages import HumanMessage, AIMessage
from agents.agent6_fairness import fairness_logging_node
import agents.agent6_fairness as agent6

def test_fairness_logging_node(monkeypatch, tmp_path):
    """测试审计日志能否正确创建并写入文件"""
    
    # 将日志文件路径重定向到 pytest 提供的临时目录 tmp_path
    mock_log_file = tmp_path / "mock_audit_logs.json"
    monkeypatch.setattr(agent6, "LOG_FILE", str(mock_log_file))
    
    state = {
        "messages": [
            HumanMessage(content="推荐个键盘"),
            AIMessage(content="推荐 Keychron K3")
        ],
        "next_agent": "Agent 2",
        "is_safe": True,
        "trace": ["Router", "RAG"]
    }
    
    result = fairness_logging_node(state)
    
    # 验证 trace 被更新
    assert "📝 Agent 6 (Audit)" in result["trace"][-1]
    
    # 验证文件被成功创建并且写入了合法的 JSON 数据
    assert mock_log_file.exists()
    
    with open(mock_log_file, "r", encoding="utf-8") as f:
        logs = json.load(f)
        assert len(logs) == 1
        assert logs[0]["user_input"] == "推荐个键盘"
        assert logs[0]["final_output"] == "推荐 Keychron K3"
        assert logs[0]["security_passed"] is True
