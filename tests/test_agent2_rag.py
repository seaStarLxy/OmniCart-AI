from langchain_core.documents import Document
from agents.agent2_rag import _build_recommendation, _extract_price, _extract_name

def test_extract_helpers():
    """测试内部提取文本的辅助函数"""
    text = "Logitech MX Master 3S wireless mouse: ergonomic design. Price: RMB 799."
    assert _extract_name(text) == "Logitech MX Master 3S wireless mouse"
    assert _extract_price(text) == "RMB 799."

def test_build_recommendation_empty_docs():
    """测试当没有检索到任何文档时的兜底回复"""
    result = _build_recommendation("推荐个鼠标", [])
    assert "I do not have a strong product match" in result

def test_build_recommendation_single_doc():
    """测试单文档的推荐组装，并命中 music 关键词分支"""
    docs = [
        Document(page_content="Sony WH-1000XM5: active noise cancellation, 30-hour battery. Price: RMB 2699.")
    ]
    # query 中包含 "music"，应该触发特定的建议
    result = _build_recommendation("I want to listen to music", docs)
    
    assert "Sony WH-1000XM5" in result
    assert "RMB 2699." in result
    assert "prioritize active noise cancellation" in result  # 验证关键词分支被正确触发

def test_build_recommendation_multiple_docs():
    """测试多文档的推荐组装，并命中 office 关键词分支"""
    docs = [
        Document(page_content="Keychron K3 Pro: lightweight and portable. Price: RMB 699."),
        Document(page_content="Logitech MX Master 3S: perfect for office work. Price: RMB 799.")
    ]
    # query 中包含 "office"，应该触发办公分支
    result = _build_recommendation("need setup for office", docs)
    
    assert "My top recommendation is Keychron K3 Pro" in result
    assert "Alternative option: Logitech MX Master 3S" in result
    assert "For productivity use" in result # 验证办公关键词分支
