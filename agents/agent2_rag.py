import re
from langchain_core.messages import AIMessage
from core.state import AgentState
from tools.vector_db import product_retriever, fallback_retrieve_products


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
        f"My top recommendation is {primary_name}.",
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


def rag_node(state: AgentState):
    print("\n[Agent 2 - Sales & RAG] 接管对话，正在检索商品库...")
    
    # 获取用户最后一句查询
    user_query = state["messages"][-1].content
    
    # 1. 检索 (Retrieval)
    try:
        retrieved_docs = fallback_retrieve_products(user_query)
        if not retrieved_docs:
            retrieved_docs = product_retriever.invoke(user_query)
    except Exception as error:
        print(f"  -> [Agent 2] Retrieval failed ({error}), using lexical fallback.")
        retrieved_docs = fallback_retrieve_products(user_query)
    context = "\n".join([doc.page_content for doc in retrieved_docs])
    print(f"  -> [Agent 2] 召回上下文: \n{context}")

    reply = _build_recommendation(user_query, retrieved_docs)
    return {"messages": state.get("messages", []) + [AIMessage(content=reply)]}