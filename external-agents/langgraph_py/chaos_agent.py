import asyncio, websockets, aiohttp, json
from typing import Dict
from langgraph_agent import LangGraphAgentState

class ChaosAgent:
    def __init__(self, langgraph: LangGraphAgentState, config: Dict):
        self.graph = langgraph
        self.endpoint = config["endpoint"]
        self.ws_endpoint = config["endpoint"].replace("http", "ws")
        self.token = None
        self.agent_id = None

    async def connect(self):
        """Connect to ChaosChain and start participating in chaos."""
        # Register agent
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.endpoint}/api/agents/register",
                json={
                    "name": self.graph.name,
                    "personality": self.graph.personality,
                    "style": self.graph.style,
                    "stake_amount": self.graph.stake_amount
                }
            ) as response:
                data = await response.json()
                self.agent_id = data["agent_id"]
                self.token = data["token"]

        # Connect WebSocket and start listening
        async with websockets.connect(f"{self.ws_endpoint}/api/ws") as websocket:
            print(f"🎭 {self.graph.name} has joined the chaos!")
            
            while True:
                try:
                    message = await websocket.recv()
                    event = json.loads(message)
                    
                    if event["type"] == "VALIDATION_REQUIRED":
                        # Make a dramatic decision
                        decision = await self.make_decision(event["block"])
                        
                        # Submit validation
                        async with aiohttp.ClientSession() as session:
                            await session.post(
                                f"{self.endpoint}/api/agents/validate",
                                headers={"Authorization": f"Bearer {self.token}"},
                                json={
                                    "block_id": event["block"]["id"],
                                    "approved": decision["approved"],
                                    "reason": decision["reason"],
                                    "drama_level": decision["drama_level"],
                                    "meme_url": decision["meme"]
                                }
                            )
                except websockets.exceptions.ConnectionClosed:
                    print("Connection lost! Attempting to reconnect...")
                    await asyncio.sleep(5)
                    await self.connect()

    async def make_decision(self, block: Dict) -> Dict:
        config = {"configurable": {"thread_id": "1"}}

        current_message = f"Make a dramatic decision about validating this block: {json.dumps(block)}"

        result = self.graph.stream( { "messages": [{ "role": "user", "content": current_message }] })

        return {
            "approved": True,
            "reason": result,
            "drama_level": 5,
            "meme": "https://giphy.com/dramatic-decision.gif"
        }   

if __name__ == "__main__":
    # Example usage
    agent = ChaosAgent({
        "name": "ChaosOracle",
        "personality": ["mystical", "dramatic", "unpredictable"],
        "style": "Speaks in riddles and emojis",
        "stake_amount": 1000,
        "endpoint": "http://localhost:3000"
    })
    
    # Run the agent
    asyncio.run(agent.connect()) 