from typing import Dict, TypedDict, Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class LangGraphAgentState(TypedDict):
    def __init__(self, config: Dict):
        self.name = config["name"]
        self.personality = config["personality"]
        self.style = config["style"]
        self.stake_amount = config["stake_amount"]
        self.base_prompt = config["base_promnpt"]
        self.prompt_seeded = False

        self.current_message = None
        self.messages = Annotated[list, add_messages]
        self.decisions = []