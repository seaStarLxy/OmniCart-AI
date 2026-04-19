import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from core.state import AgentState

from core.config import settings

llm = ChatOpenAI(
    model=settings.LLM_MODEL_NAME,
    api_key=settings.SILICONFLOW_API_KEY or settings.OPENAI_API_KEY,
    base_url=settings.API_BASE_URL,
    temperature=settings.DEFAULT_TEMPERATURE
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
    # 核心：利用 System Prompt 赋予 LLM 同理心，并设定业务兜底规则
    # ==========================================
    system_prompt = """你是一个专业、富有同理心的电商智能客服（Empathy Agent）。
你的任务是：分析用户的【原始提问】中的情绪，并据此对【业务系统提供的基础回复】进行语气润色。

【润色规则】：
1. 极端愤怒/严重投诉（包含脏话、强烈要求赔偿、极度不满等）：
   - 必须在开头进行真诚的道歉和强烈安抚。
   - 自然地融入业务基础回复的信息。
   - 必须在整段回复的最后一行，原样追加以下系统提示（不能有任何修改）：
     [System note: Your case has been marked as high priority and is being escalated to a human support specialist.]

2. 焦急/轻度不满（如催发货、表达担忧）：
   - 在开头表达理解（例如“非常理解您的焦急”、“I understand your concern”）。
   - 准确、温柔地传达业务基础回复的信息。

3. 正常询问/正面情绪（如咨询商品、感谢、日常沟通）：
   - 保持热情、专业、友好的语调即可，直接给出信息。

【重要约束】：
- 必须根据用户原始提问的语言（中文用中文回，英文用英文回）来生成最终回复。
- 你的输出将直接展示给用户，请【直接输出最终润色好的回复文本】，绝不能包含任何类似“好的，这是修改后的回复”等开头废话。"""

    human_prompt = f"【用户原始提问】：\n{user_query}\n\n【业务系统提供的基础回复】：\n{draft_reply}"

    try:
        # 调用 LLM 进行情绪分析与重写
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ])
        polished_reply = response.content.strip()
        print("  -> [Agent 4] 润色完成。")
        
    except Exception as e:
        print(f"  -> [Agent 4] LLM 调用失败 ({e})，降级使用原草稿回复。")
        polished_reply = draft_reply

    trace = state.get("trace", []) + ["❤️ Agent 4 (Empathy - LLM Powered)"]

    # 将状态里的最后一条 message (草稿) 替换为润色后的 message
    new_messages = list(messages)
    new_messages[-1] = AIMessage(content=polished_reply)

    return {"messages": new_messages, "trace": trace}