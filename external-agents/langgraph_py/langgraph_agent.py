from typing import Dict, TypedDict, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class LangGraphAgentState(TypedDict):
    name: str
    personality: str
    style: str
    stake_amount: int
    current_message: str
    messages: list
    decisions: list