from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from core.config import settings
from core.state import AgentState

llm = ChatOpenAI(
    model=settings.LLM_MODEL_NAME,
    api_key=settings.SILICONFLOW_API_KEY or settings.OPENAI_API_KEY,
    base_url=settings.API_BASE_URL,
    temperature=settings.DEFAULT_TEMPERATURE
)

def triage_router_node(state: AgentState) -> dict:
    user_input = state["messages"][-1]
    # 提取用户真正说的文本
    content = user_input.content if hasattr(user_input, "content") else str(user_input)
    print(f"\n[Agent 1 - Router] 正在利用大模型分析输入意图: {content}")

    # ==========================================
    # 核心：利用 System Prompt 让 LLM 进行推理 (Reasoning)
    # ==========================================
    system_prompt = """你是一个智能电商客服系统的路由(Router)决策大脑。
请分析用户的输入意图，并将其精确分类到以下两个智能体之一：

1. 如果用户的意图是：查询订单状态、追踪物流轨迹、申请退换货、售后投诉，或者提供了类似 "ORD-12345678-123" 的订单号。
   -> 请仅回复："Agent 3"

2. 如果用户的意图是：寻求商品推荐、询问商品参数、比较商品、寻找特定功能/价格段的产品等导购需求。
   -> 请仅回复："Agent 2"

【严格约束】：你的输出只能是 "Agent 2" 或 "Agent 3"，不能包含任何其他标点符号或解释性文字。"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=content)
    ]

    try:
        # 调用大模型进行意图推理
        response = llm.invoke(messages)
        decision_text = response.content.strip()
        print(f"  -> [Agent 1] 大模型原始输出: {decision_text}")
    except Exception as e:
        print(f"  -> [Agent 1] LLM 调用失败 ({e})，降级回退到 Agent 2")
        decision_text = "Agent 2"

    # ==========================================
    # 解析 LLM 输出并路由
    # ==========================================
    if "Agent 3" in decision_text:
        decision = "Agent 3 (Order Management)"
    else:
        # 默认回退到导购推荐 (RAG)
        decision = "Agent 2 (Sales & RAG)"

    print(f"[Agent 1 - Router] 最终决定路由至: {decision}")
    trace = state.get("trace", []) + ["🧭 Agent 1 (Router - LLM Powered)"]
    return {"next_agent": decision, "trace": trace}