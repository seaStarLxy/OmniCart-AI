from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from core.state import AgentState
from tools.mock_apis import check_order_status

# 初始化大模型并绑定工具
# llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
llm = ChatOpenAI(
    temperature=0, # 注意：每个 Agent 原来的 temperature 不同，请保留原值 (Agent 4 是 0.5，Agent 2 是 0.3)
    model="Qwen/Qwen2.5-7B-Instruct", # 推荐使用 Qwen 2.5 或其他支持 Tool Calling 的优秀开源模型
    openai_api_base="https://api.siliconflow.cn/v1",
    openai_api_key="apikey", # 这里填入你在 vector_db.py 中使用的密钥
    max_tokens=2048 # 建议加上最大 token 限制以防截断
)
tools = [check_order_status]
llm_with_tools = llm.bind_tools(tools)

def order_node(state: AgentState):
    print("\n[Agent 3 - Order Management] 接管对话，思考中...")
    messages = state.get("messages", [])
    
    # 给 Agent 3 注入身份和职责
    sys_msg = SystemMessage(
        content="你是 OmniCart-AI 的订单管理助手 (Agent 3)。"
                "如果用户要查订单，你必须使用 check_order_status 工具。"
                "如果用户没有提供订单号，请礼貌地向用户索要订单号，不要瞎编。"
    )
    
    # 让大模型结合历史消息和工具进行推理
    response = llm_with_tools.invoke([sys_msg] + messages)
    
    # 将大模型的回复追加到消息历史中
    return {"messages": [response]}