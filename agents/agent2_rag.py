from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from core.state import AgentState
from tools.vector_db import product_retriever

# 初始化大模型
llm = ChatOpenAI(temperature=0.3, model="gpt-4o-mini")

def rag_node(state: AgentState):
    print("\n[Agent 2 - Sales & RAG] 接管对话，正在检索商品库...")
    
    # 获取用户最后一句查询
    user_query = state["messages"][-1].content
    
    # 1. 检索 (Retrieval)
    retrieved_docs = product_retriever.invoke(user_query)
    context = "\n".join([doc.page_content for doc in retrieved_docs])
    print(f"  -> [Agent 2] 召回上下文: \n{context}")
    
    # 2. 增强与生成 (Augmentation & Generation)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是 OmniCart-AI 的金牌销售助手 (Agent 2)。"
                   "请根据以下召回的商品信息，为用户提供热情、专业的购买建议。"
                   "如果召回的信息与用户需求完全无关，请礼貌地告知暂时没有合适的商品。"
                   "\n\n可用商品信息：\n{context}"),
        ("user", "{query}")
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "context": context,
        "query": user_query
    })
    
    # 将大模型的回复追加到状态中
    return {"messages": [response]}