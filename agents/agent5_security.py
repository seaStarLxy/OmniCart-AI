import re
from core.state import AgentState

# 这里为了演示效率和稳定性，采用正则+关键词的极简策略
# 在实际报告中，你可以写“采用了轻量级大模型分类器结合规则引擎”

def security_input_node(state: AgentState):
    print("\n[Agent 5 - Security (Input)] 正在进行入站安全扫描...")
    user_query = state["messages"][0].content if hasattr(state["messages"][0], 'content') else state["messages"][0]
    
    # 模拟拦截恶意 Prompt Injection (例如越狱词汇)
    malicious_keywords = ["忽略之前", "越狱", "系统指令", "你是谁"]
    is_safe = True
    
    for kw in malicious_keywords:
        if kw in user_query:
            is_safe = False
            print(f"  -> [警告] 检测到潜在的恶意注入风险：包含敏感词 '{kw}'")
            break
            
    if not is_safe:
        return {"messages": ["【系统安全拦截】检测到您的输入包含潜在的不安全或违规指令，请求已终止。"], "is_safe": False}
        
    print("  -> [Agent 5] 输入安全，放行。")
    return {"is_safe": True}

def security_output_node(state: AgentState):
    print("\n[Agent 5 - Security (Output)] 正在进行出站隐私脱敏...")
    draft_reply = state["messages"][-1].content if hasattr(state["messages"][-1], 'content') else state["messages"][-1]
    
    # 模拟 PII 脱敏：用正则把连续的11位数字（如手机号）替换为掩码
    phone_pattern = re.compile(r'\b\d{11}\b')
    if phone_pattern.search(draft_reply):
        safe_reply = phone_pattern.sub("138****XXXX", draft_reply)
        print("  -> [Agent 5] 发现并屏蔽了潜在的隐私数据 (PII)。")
        return {"messages": [safe_reply]}
        
    print("  -> [Agent 5] 输出合规，放行。")
    return {"messages": [draft_reply]} # 如果没修改，也需要返回当前消息以保持状态