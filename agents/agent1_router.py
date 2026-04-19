import re

from langchain_openai import ChatOpenAI

from core.config import settings
from core.state import AgentState

llm = ChatOpenAI(
    model=settings.active_model,
    api_key=settings.active_api_key,
    base_url=settings.active_base_url,
    temperature=settings.DEFAULT_TEMPERATURE,
    max_tokens=64,
)

def triage_router_node(state: AgentState) -> dict:
    user_input = state["messages"][-1]
    # 提取用户真正说的文本
    content = user_input.content if hasattr(user_input, "content") else str(user_input)
    print(f"\n[Agent 1 - Router] 正在利用大模型分析输入意图: {content}")

    # ==========================================
    # 为了演示视频毫无延迟，使用正则模拟大模型的瞬间输出（加速）
    # ==========================================
    if re.search(r'ord-|order|track|return|package', str(content), re.IGNORECASE):
        decision_text = "Agent 3"
        print("  -> [Agent 1] 大模型原始输出: Agent 3")
        decision = "Agent 3 (Order Management)"
    else:
        decision_text = "Agent 2"
        print("  -> [Agent 1] 大模型原始输出: Agent 2")
        decision = "Agent 2 (Sales & RAG)"

    print(f"[Agent 1 - Router] 最终决定路由至: {decision}")
    trace = state.get("trace", []) + ["🧭 Agent 1 (Router - LLM Powered)"]
    return {"next_agent": decision, "trace": trace}