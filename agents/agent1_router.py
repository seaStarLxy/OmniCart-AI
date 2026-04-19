
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

ROUTER_PROMPT = """You are a routing agent for an e-commerce support system.
Analyze the user's message and decide which agent should handle it.

Rules:
- If the message is about tracking, returning, or managing an order (contains order IDs, shipping, delivery, package status, etc.), respond with exactly: Agent 3
- For everything else (product questions, recommendations, general inquiries), respond with exactly: Agent 2

Respond with ONLY "Agent 2" or "Agent 3", nothing else.

User message: {user_input}"""


def triage_router_node(state: AgentState) -> dict:
    user_input = state["messages"][-1]
    content = user_input.content if hasattr(user_input, "content") else str(user_input)
    print(f"\n[Agent 1 - Router] 正在利用大模型分析输入意图: {content}")

    prompt = ROUTER_PROMPT.format(user_input=content)
    response = llm.invoke(prompt)
    decision_text = response.content.strip()
    print(f"  -> [Agent 1] 大模型原始输出: {decision_text}")

    # 解析 LLM 输出，容错处理
    if "3" in decision_text:
        decision = "Agent 3 (Order Management)"
    else:
        decision = "Agent 2 (Sales & RAG)"

    print(f"[Agent 1 - Router] 最终决定路由至: {decision}")
    trace = state.get("trace", []) + ["🧭 Agent 1 (Router - LLM Powered)"]
    return {"next_agent": decision, "trace": trace}