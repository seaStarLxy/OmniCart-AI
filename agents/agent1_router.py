import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from core.state import AgentState

# 初始化 LLM 模型 (展示时可以用 gpt-4o 或 gpt-4o-mini)
# 只要环境变量里有 OPENAI_API_KEY，它就会自动读取
llm = ChatOpenAI(
    temperature=0, # 注意：每个 Agent 原来的 temperature 不同，请保留原值 (Agent 4 是 0.5，Agent 2 是 0.3)
    model="Qwen/Qwen2.5-7B-Instruct", # 推荐使用 Qwen 2.5 或其他支持 Tool Calling 的优秀开源模型
    openai_api_base="https://api.siliconflow.cn/v1",
    openai_api_key="apikey", # 这里填入你在 vector_db.py 中使用的密钥
    max_tokens=2048 # 建议加上最大 token 限制以防截断
)

def triage_router_node(state: AgentState) -> dict:
    user_input = state["messages"][-1]
    print(f"\n[Agent 1 - Router] 正在利用大模型分析输入: {user_input}")

    # 定义系统提示词
    prompt = PromptTemplate.from_template(
        """你是一个智能电商客服路由中心（Agent 1）。
        请分析用户的输入，决定将其路由给哪个专业的 Agent。
        
        规则：
        - 如果用户询问订单状态、退款、发货进度等，请严格输出："Agent 3 (Order Management)"
        - 如果用户寻求商品推荐、产品信息、购物建议等，请严格输出："Agent 2 (Sales & RAG)"
        - 只能输出以上两个选项之一，不要包含任何其他文字。

        用户输入: {input}
        """
    )
    
    # 组装调用链
    chain = prompt | llm
    
    try:
        # 尝试调用大模型
        response = chain.invoke({"input": user_input})
        decision = response.content.strip()
    except Exception as e:
        # 如果你没配置 API Key 或者网络不通，走这个降级策略保证服务不死
        print(f"[Agent 1 - Router] LLM 调用失败 ({e})，使用规则降级处理。")
        if "订单" in user_input or "退款" in user_input:
            decision = "Agent 3 (Order Management) [Fallback]"
        else:
            decision = "Agent 2 (Sales & RAG) [Fallback]"

    print(f"[Agent 1 - Router] 决定路由至: {decision}")
    return {"next_agent": decision}