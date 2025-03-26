from typing import Dict, TypedDict, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    name: str
    personality: str
    style: str
    current_prompt: str
    prompts: list[str]
    feed_responses: list[str]
    decisions_reasoning: list[str]
    decisions: dict