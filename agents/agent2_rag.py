import re

from langchain_core.messages import AIMessage

from core.state import AgentState
from tools.vector_db import fallback_retrieve_products, get_product_retriever


def _extract_price(product_text: str) -> str:
    match = re.search(r"price:\s*rmb\s*([\d.]+)", product_text, re.IGNORECASE)
    if match:
        return f"RMB {match.group(1)}"
    return "Price unavailable"


def _extract_name(product_text: str) -> str:
    return product_text.split(":", 1)[0].strip()


def _extract_features(product_text: str) -> str:
    parts = product_text.split(":", 1)
    if len(parts) < 2:
        return product_text.strip()
    feature_text = parts[1].strip()
    feature_text = re.sub(r"price:\s*rmb\s*[\d.]+\.?", "", feature_text, flags=re.IGNORECASE).strip()
    return feature_text.rstrip(".")


def _build_recommendation(query: str, docs) -> str:
    if not docs:
        return "I do not have a strong product match for that request yet. If you share your budget or preferred brand, I can narrow it down."

    primary = docs[0].page_content
    primary_name = _extract_name(primary)
    primary_features = _extract_features(primary)
    primary_price = _extract_price(primary)

    lines = [
        f"Based on your request, here is the product I recommend: {primary_name}.",
        f"It is a strong fit for your request because {primary_features}.",
        f"Price: {primary_price}."
    ]

    if len(docs) > 1:
        secondary = docs[1].page_content
        secondary_name = _extract_name(secondary)
        secondary_features = _extract_features(secondary)
        secondary_price = _extract_price(secondary)
        lines.append(f"Alternative option: {secondary_name} ({secondary_price}) for {secondary_features}.")

    if any(keyword in query.lower() for keyword in ["music", "call", "noise", "headphone", "headset"]):
        lines.append("For your use case, I would prioritize active noise cancellation, call clarity, comfort, and battery life.")
    elif any(keyword in query.lower() for keyword in ["office", "work", "productivity", "coding", "keyboard", "mouse"]):
        lines.append("For productivity use, I would prioritize comfort, reliability, and day-to-day usability over flashy extras.")

    return "\n\n".join(lines)


# Step 1: Planning Loop - 规划检索策略 (ReAct思想的微型体现)
def _plan_search_strategy(user_query: str) -> dict:
    """分析用户查询，规划检索范围和降级策略 (Planning Loop)"""
    strategy = {
        "is_technical": any(keyword in user_query.lower() for keyword in ["keyboard", "mouse", "office"]),
        "is_budget_conscious": any(keyword in user_query.lower() for keyword in ["cheap", "budget", "便宜", "预算", "性价比"]),
        "search_count": 3 if "比较" in user_query or "alternatives" in user_query.lower() else 2
    }
    return strategy

def _execute_and_evaluate(user_query: str, strategy: dict) -> list:
    """执行带有反馈循环的条件检索"""
    # 执行初次检索
    docs = fallback_retrieve_products(user_query, k=strategy["search_count"])
    
    # 评估循环：如果用户在意预算，但检索出来的内容没有价格信息，则必须扩大检索范围
    if strategy["is_budget_conscious"] and not docs:
        print("  -> [Agent 2] 检索评估未命中，触发重新规划检索关键词...")
        # 降级或调整关键词
        return fallback_retrieve_products("廉价 " + user_query, k=2)
    return docs

def rag_node(state: AgentState):
    print("\n[Agent 2 - Sales & RAG] 接管对话，启动商品发现与规划循环...")
    
    user_query = state["messages"][-1].content
    
    # 1. 规划循环 (Planning)
    strategy = _plan_search_strategy(user_query)
    print(f"  -> [Agent 2] 规划搜索策略: {strategy}")
    
    # 2. 执行与评估循环 (Execution & Evaluation)
    try:
        retrieved_docs = _execute_and_evaluate(user_query, strategy)
        if not retrieved_docs:
            retriever = get_product_retriever()
            retrieved_docs = retriever.invoke(user_query)
    except Exception as error:
        print(f"  -> [Agent 2] 检索失败 ({error})，进入降级搜索回调。")
        retrieved_docs = fallback_retrieve_products(user_query)
        
    context = "\n".join([doc.page_content for doc in retrieved_docs])
    print(f"  -> [Agent 2] 召回上下文: \n{context}")

    reply = _build_recommendation(user_query, retrieved_docs)
    trace = state.get("trace", []) + ["🔍 Agent 2 (RAG with Planning Loop)"]
    
    # 抽取检索到的文本作为事实核验上下文
    context_str = "\n".join([doc.page_content for doc in retrieved_docs]) if retrieved_docs else ""
    return {
        "messages": state.get("messages", []) + [AIMessage(content=reply)], 
        "trace": trace,
        "context": context_str
    }