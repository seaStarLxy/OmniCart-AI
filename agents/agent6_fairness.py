import json
import os
from datetime import datetime
from core.state import AgentState

LOG_FILE = "logs/audit_logs.json"

def fairness_logging_node(state: AgentState):
    print("\n[Agent 6 - Fairness & Explainability] 正在生成审计日志...")
    
    user_query = state["messages"][0].content if hasattr(state["messages"][0], 'content') else state["messages"][0]
    final_reply = state["messages"][-1].content if hasattr(state["messages"][-1], 'content') else state["messages"][-1]
    
    # 构造符合 IMDA 要求的审计记录
    audit_record = {
        "timestamp": datetime.now().isoformat(),
        "user_input": user_query,
        "routing_decision": state.get("next_agent", "N/A"),
        "security_passed": state.get("is_safe", False),
        "final_output": final_reply,
        "bias_check_flag": "Passed" # 演示用：默认公平性审查通过
    }
    
    # 追加写入本地 JSON 文件
    logs = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                pass
                
    logs.append(audit_record)
    
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=4)
        
    print(f"  -> [Agent 6] 审计日志已保存至 {LOG_FILE}。")
    trace = state.get("trace", []) + ["📝 Agent 6 (Audit)"]
    return {"trace": trace} # 仅仅是旁路记录，不改变流转状态