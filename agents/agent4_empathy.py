import re
from langchain_core.messages import AIMessage
from core.state import AgentState


def _contains_any(text: str, keywords):
    return any(keyword in text for keyword in keywords)


def _contains_english_emotion(text: str, keywords):
    return any(re.search(rf"\b{re.escape(keyword)}\b", text) for keyword in keywords)

def empathy_node(state: AgentState):
    print("\n[Agent 4 - Empathy] 正在进行情绪分析与语气润色...")
    
    # 获取用户的原始问题 (列表里的第一个消息)
    
    messages = state.get("messages", [])
    user_query = ""
    for msg in reversed(messages[:-1]):
        if getattr(msg, "type", "") == "human" or getattr(msg, "role", "") == "user":
            user_query = msg.content if hasattr(msg, "content") else str(msg)
            break
    if not user_query:
        if messages:
            user_query = messages[0].content if hasattr(messages[0], "content") else str(messages[0])
        else:
            user_query = ""

    
    # 获取 Agent 2 或 Agent 3 生成的草稿回复 (列表里的最后一个消息)
    draft_reply = state["messages"][-1].content if hasattr(state["messages"][-1], 'content') else state["messages"][-1]

    normalized = user_query.lower()
    extreme_cn_keywords = ["垃圾", "投诉", "赔偿", "爆粗口"]
    extreme_en_keywords = ["idiot", "stupid", "angry", "furious", "terrible", "complaint"]
    upset_cn_keywords = ["着急", "不满", "抱怨", "生气", "很急", "焦急"]
    upset_en_keywords = ["worry", "worried", "upset", "anxious", "frustrated"]

    polished_reply = draft_reply.strip()
    if _contains_any(normalized, extreme_cn_keywords) or _contains_english_emotion(normalized, extreme_en_keywords):
        polished_reply = (
            "I understand that this is very frustrating, and I am sorry for the inconvenience.\n\n"
            f"{polished_reply}\n\n"
            "[System note: Your case has been marked as high priority and is being escalated to a human support specialist.]"
        )
    elif _contains_any(normalized, upset_cn_keywords) or _contains_english_emotion(normalized, upset_en_keywords):
        polished_reply = (
            "I understand your concern, and I am sorry for the inconvenience.\n\n"
            f"{polished_reply}"
        )

    print("  -> [Agent 4] 润色完成。")
    trace = state.get("trace", []) + ["❤️ Agent 4 (Empathy)"]
    return {"messages": state.get("messages", []) + [AIMessage(content=polished_reply)], "trace": trace}