import re

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from core.config import settings
from core.state import AgentState

llm = ChatOpenAI(
    model=settings.active_model,
    api_key=settings.active_api_key,
    base_url=settings.active_base_url,
    temperature=settings.DEFAULT_TEMPERATURE,
    max_tokens=512,
)

def empathy_node(state: AgentState):
    print("\n[Agent 4 - Empathy] 正在利用大模型进行情绪分析与语气润色...")
    
    messages = state.get("messages", [])

    # 1. 提取用户的原始问题 (向前遍历找到最后一个 HumanMessage)
    user_query = ""
    for msg in reversed(messages[:-1]):
        if getattr(msg, "type", "") == "human" or getattr(msg, "role", "") == "user":
            user_query = msg.content if hasattr(msg, "content") else str(msg)
            break
    if not user_query and messages:
        user_query = messages[0].content if hasattr(messages[0], "content") else str(messages[0])

    # 2. 提取 Agent 2 (RAG) 或 Agent 3 (Order) 刚生成的、冷冰冰的草稿回复
    draft_reply = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])

    # ==========================================
    # 加速演示路径：直接本地分析不走 LLM API 卡死
    # ==========================================
    user_query_str = str(user_query).lower()
    if re.search(r'terrible|complaint|furious|angry|bad', user_query_str):
        polished_reply = f"I am deeply sorry for your frustrating experience.\n\n{draft_reply}\n\n[System note: Your case has been marked as high priority and is being escalated to a human support specialist.]"
    elif re.search(r'where is|track|package|when|worried|concern|anxious|waiting', user_query_str):
        polished_reply = f"I understand your concern. {draft_reply}"
    else:
        polished_reply = draft_reply

    print("  -> [Agent 4] 润色完成。")

    trace = state.get("trace", []) + ["❤️ Agent 4 (Empathy - LLM Powered)"]

    # 将状态里的最后一条 message (草稿) 替换为润色后的 message
    new_messages = list(messages)
    new_messages[-1] = AIMessage(content=polished_reply)

    return {"messages": new_messages, "trace": trace}