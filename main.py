from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage

from core.state import AgentState
from agents.agent1_router import triage_router_node
from agents.agent3_order import order_node
from agents.agent2_rag import rag_node
from agents.agent4_empathy import empathy_node
from agents.agent5_security import security_input_node, security_output_node # 新增
from agents.agent6_fairness import fairness_logging_node

app = FastAPI(title="OmniCart-AI", version="0.3.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)
# ==========================================
# 构建 LangGraph 状态图
# ==========================================
workflow = StateGraph(AgentState)

# 1. 注册全部 6 个 Agent 的节点 (共 7 个 Node，因为 Agent5 拆成了进出两头)
workflow.add_node("sec_in", security_input_node)
workflow.add_node("router", triage_router_node)
workflow.add_node("order_agent", order_node)
workflow.add_node("rag_agent", rag_node)
workflow.add_node("empathy_agent", empathy_node)
workflow.add_node("sec_out", security_output_node)
workflow.add_node("logger", fairness_logging_node)

# 2. 定义安全网关的条件路由
def check_safety(state: AgentState):
    if state.get("is_safe"):
        return "router" # 安全，进主业务
    else:
        return "logger" # 不安全，直接去写日志然后结束

# 3. 定义业务网关的条件路由
def route_decision(state: AgentState):
    if "Agent 3" in state["next_agent"]:
        return "order_agent"
    return "rag_agent"

# ==========================================
# 4. 缝合完整工作流 (The Master Pipeline)
# ==========================================
# 入口 -> 安全查杀 -> (如果不安全，直达日志) -> (如果安全，进路由)
workflow.set_entry_point("sec_in")
workflow.add_conditional_edges("sec_in", check_safety, {"router": "router", "logger": "logger"})

# 路由 -> (分发给具体的干活 Agent)
workflow.add_conditional_edges("router", route_decision, {"order_agent": "order_agent", "rag_agent": "rag_agent"})

# 干活 Agent -> 情绪润色
workflow.add_edge("order_agent", "empathy_agent")
workflow.add_edge("rag_agent", "empathy_agent")

# 情绪润色 -> 出口脱敏
workflow.add_edge("empathy_agent", "sec_out")

# 出口脱敏 -> 写入日志
workflow.add_edge("sec_out", "logger")

# 写完日志 -> 流程结束
workflow.add_edge("logger", END)

app_graph = workflow.compile()

# ==========================================
# FastAPI 接口
# ==========================================
@app.post("/chat")
async def chat_endpoint(query: str):
    # 转换为 LangChain 标准的消息对象
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "next_agent": ""
    }
    
    # 执行状态图
    result = app_graph.invoke(initial_state)
    
    # 获取最后一条消息作为输出（增加容错：判断是对象还是纯字符串）
    last_msg = result["messages"][-1]
    final_message = last_msg.content if hasattr(last_msg, 'content') else last_msg
    
    return {
        "status": "success",
        "routing": result["next_agent"],
        "reply": final_message
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)