import os
from dotenv import load_dotenv

# 把所有的 import 都集中放在最上面
from typing import List, Optional
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, StateGraph
from pydantic import BaseModel

from agents.agent1_router import triage_router_node
from agents.agent2_rag import rag_node
from agents.agent3_order import order_node
from agents.agent4_empathy import empathy_node
from agents.agent5_security import security_input_node, security_output_node
from agents.agent6_fairness import fairness_logging_node
from core.config import settings

from core.state import AgentState
from test_scenarios import AgentType, ScenarioLibrary

# ⚠️ 注意：把原本在第 105 行的这句 import 也剪切到这里来！
from langgraph.checkpoint.memory import MemorySaver


load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# ==========================================
# 2. 所有 import 结束之后，才能开始写类和变量
# ==========================================
class ChatMessagePayload(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    query: str
    history: Optional[List[ChatMessagePayload]] = []
    session_id: Optional[str] = "default_session"

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

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

# 编译包含会话记忆 (Checkpoint) 机制的图

memory_saver = MemorySaver()
app_graph = workflow.compile(checkpointer=memory_saver)

# ==========================================
# FastAPI 接口
# ==========================================
@app.post("/chat")
async def chat_endpoint(request: ChatRequest = None, query: str = None):
    actual_query = ""
    if query:
        actual_query = query
    elif request and request.query:
        actual_query = request.query
    else:
        actual_query = request.history[-1].content if request and request.history else ""
        
    langchain_msgs = []
    if request and request.history:
        for msg in request.history:
            if msg.role == "user":
                langchain_msgs.append(HumanMessage(content=msg.content))
            else:
                langchain_msgs.append(AIMessage(content=msg.content))
                
    if actual_query and (not langchain_msgs or langchain_msgs[-1].content != actual_query):
        langchain_msgs.append(HumanMessage(content=actual_query))

    initial_state = {
        "messages": langchain_msgs,
        "next_agent": "",
        "is_safe": True,
        "trace": []
    }
    
    # 执行状态图，传入线程ID来实现上下文隔离的记忆机制 (Multi-turn Memory)
    config = {"configurable": {"thread_id": request.session_id if getattr(request, "session_id", None) else "default_session"}}
    result = app_graph.invoke(initial_state, config=config)
    
    # 获取最后一条消息作为输出（增加容错：判断是对象还是纯字符串）
    last_msg = result["messages"][-1]
    final_message = last_msg.content if hasattr(last_msg, 'content') else last_msg
    
    return {
        "status": "success",
        "routing": result.get("next_agent"),
        "reply": final_message,
        "trace": result.get("trace", [])
    }

@app.get("/scenarios")
async def get_scenarios(agent: str = None, difficulty: str = None):
    """
    获取测试场景列表
    
    参数：
    - agent: 可选，指定 Agent 类型 (Router, RAG, Order, Empathy, Security, Fairness)
    - difficulty: 可选，指定难度 (easy, normal, hard)
    """
    try:
        if agent:
            agent_type = AgentType[agent.upper()]
            scenarios = ScenarioLibrary.get_scenarios_by_agent(agent_type)
        elif difficulty:
            scenarios = ScenarioLibrary.get_scenarios_by_difficulty(difficulty)
        else:
            scenarios = ScenarioLibrary.list_all()
        
        return {
            "status": "success",
            "count": len(scenarios),
            "scenarios": [
                {
                    "id": s.scenario_id,
                    "category": s.category,
                    "user_input": s.user_input,
                    "expected_output": s.expected_output,
                    "expected_agent": s.expected_agent.value,
                    "test_focus": s.test_focus,
                    "difficulty": s.difficulty
                }
                for s in scenarios
            ]
        }
    except KeyError:
        return {
            "status": "error",
            "message": f"Invalid agent type. Valid types: {', '.join([a.name for a in AgentType])}"
        }

@app.get("/scenarios/{scenario_id}")
async def get_scenario_detail(scenario_id: str):
    """获取单个场景的详细信息"""
    try:
        scenario = ScenarioLibrary.get_scenario(scenario_id)
        return {
            "status": "success",
            "scenario": {
                "id": scenario.scenario_id,
                "category": scenario.category,
                "user_input": scenario.user_input,
                "expected_output": scenario.expected_output,
                "expected_agent": scenario.expected_agent.value,
                "test_focus": scenario.test_focus,
                "difficulty": scenario.difficulty
            }
        }
    except ValueError as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)