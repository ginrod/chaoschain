from typing import Dict, TypedDict, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    name: str
    personality: str
    style: str
    stake_amount: int
    prompts: list[str]
    decisions: list
    feed_responses: list[str]