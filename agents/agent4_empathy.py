
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

EMPATHY_PROMPT = """You are a customer-service empathy agent. Your ONLY job is to add a brief empathetic prefix to the draft reply. You must NOT reformat, rephrase, or restructure the draft reply in any way.

Strict rules:
1. If the user sounds extremely upset (words like terrible, furious, angry, complaint): prepend "I am deeply sorry for your frustrating experience." before the draft, and append "[System note: Your case has been marked as high priority and is being escalated to a human support specialist.]" at the end.
2. If the user sounds worried or anxious (words like worried, concern, where is, waiting): prepend "I understand your concern." before the draft.
3. Otherwise: return the draft reply EXACTLY as-is.
4. CRITICAL: Do NOT add markdown formatting. Do NOT use bold, bullet points, or headers. Do NOT rephrase or restructure the draft reply. Keep it EXACTLY as provided, only adding the empathetic prefix/suffix.

User's original question:
{user_query}

Draft reply (return this EXACTLY, only add prefix/suffix):
{draft_reply}

Output:"""


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

    # 2. 提取 Agent 2 (RAG) 或 Agent 3 (Order) 刚生成的草稿回复
    draft_reply = messages[-1].content if hasattr(messages[-1], 'content') else str(messages[-1])

    # 使用 LLM 进行情绪润色
    prompt = EMPATHY_PROMPT.format(user_query=user_query, draft_reply=draft_reply)
    response = llm.invoke(prompt)
    polished_reply = response.content.strip()

    print("  -> [Agent 4] 润色完成。")

    trace = state.get("trace", []) + ["❤️ Agent 4 (Empathy - LLM Powered)"]

    # 将状态里的最后一条 message (草稿) 替换为润色后的 message
    new_messages = list(messages)
    new_messages[-1] = AIMessage(content=polished_reply)

    return {"messages": new_messages, "trace": trace}