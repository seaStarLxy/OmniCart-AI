from typing import Any, List, TypedDict


class AgentState(TypedDict):
    trace: List[str]
    messages: List[Any]  # 记录对话历史
    next_agent: str      # 记录下一步该路由给谁
    is_safe: bool        # 记录当前请求是否触发了安全警报
    context: str         # 记录当前检索到的背景知识或 API 数据，供 Agent 5 做防幻觉校验