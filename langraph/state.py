from typing import NotRequired, TypedDict

class AgentState(TypedDict):
    user_query:str
    intent: NotRequired[str]
    result: NotRequired[str]
    input_allowed: NotRequired[bool]
    guardrail_reason: NotRequired[str]
    output_allowed: NotRequired[bool]

