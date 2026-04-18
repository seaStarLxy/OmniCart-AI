from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from core.state import AgentState

# 语气润色需要一点创造力，所以把 temperature 调到 0.5
# llm = ChatOpenAI(temperature=0.5, model="gpt-4o-mini")
llm = ChatOpenAI(
    temperature=0.5, # 注意：每个 Agent 原来的 temperature 不同，请保留原值 (Agent 4 是 0.5，Agent 2 是 0.3)
    model="Qwen/Qwen2.5-7B-Instruct", # 推荐使用 Qwen 2.5 或其他支持 Tool Calling 的优秀开源模型
    openai_api_base="https://api.siliconflow.cn/v1",
    openai_api_key="sk-dikkdnbuvkhmsvyoruibkhgdsobbvhbiaxlulopbrxziijwt", # 这里填入你在 vector_db.py 中使用的密钥
    max_tokens=2048 # 建议加上最大 token 限制以防截断
)

def empathy_node(state: AgentState):
    print("\n[Agent 4 - Empathy] 正在进行情绪分析与语气润色...")
    
    # 获取用户的原始问题 (列表里的第一个消息)
    user_query = state["messages"][0].content if hasattr(state["messages"][0], 'content') else state["messages"][0]
    
    # 获取 Agent 2 或 Agent 3 生成的草稿回复 (列表里的最后一个消息)
    draft_reply = state["messages"][-1].content if hasattr(state["messages"][-1], 'content') else state["messages"][-1]
    
    prompt = ChatPromptTemplate.from_messages([
            ("system", """你是 OmniCart-AI 的情绪管理专家 (Agent 4)。
            你的任务是审查系统生成的【草稿回复】，并结合用户的【原始输入】情绪进行润色。
            
            规则：
            1. 如果用户带有明显的愤怒、焦急或抱怨情绪，请在回复开头加入安抚性的话语（如“非常理解您的焦急，抱歉给您带来不便”），并使整体语气更加温和。
            2. 如果检测到用户极端愤怒、爆粗口或要求投诉，请在回复末尾强制加上：“[系统提示：已为您标记高优先级，正在转接人工客服专员为您处理。]”
            3. 如果用户情绪平稳（正常咨询），保持专业热情的语调即可，无需过度安抚。
            4. 绝对不能改变草稿回复中的核心事实数据（如商品参数、订单状态）。
            5. 【强制警告】你只能输出最终润色好的回复内容！绝对不要输出任何你的分析过程、心理活动或解释性文字（例如绝不能出现“用户情绪平稳，因此...”这种话）。"""),
            ("user", "用户的原始输入: {query}\n\n系统的草稿回复: {draft}")
        ])
    
    chain = prompt | llm
    response = chain.invoke({"query": user_query, "draft": draft_reply})
    
    print("  -> [Agent 4] 润色完成。")
    return {"messages": [response]}