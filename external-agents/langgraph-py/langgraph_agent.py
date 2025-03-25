from typing import Dict

class LangGraphAgentState():
    def __init__(self, config: Dict):
        self.name = config["name"]
        self.personality = config["personality"]
        self.style = config["style"]
        self.stake_amount = config["stake_amount"]
        self.base_prompt = config["base_promnpt"]
        self.prompt_seeded = False