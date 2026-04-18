from typing import TypedDict, List, Any

class AgentState(TypedDict):
    trace: List[str]
    messages: List[Any]  # 记录对话历史
    next_agent: str      # 记录下一步该路由给谁
    is_safe: bool        # 【新增】记录当前请求是否触发了安全警报