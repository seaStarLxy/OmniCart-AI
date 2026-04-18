from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from core.state import AgentState
from tools.mock_apis import check_order_status

# 初始化大模型并绑定工具
llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
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