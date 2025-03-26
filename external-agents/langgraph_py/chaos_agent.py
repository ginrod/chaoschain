import asyncio, websockets, aiohttp, json
from typing import Dict

class ChaosAgent:
    def __init__(self, state_graph, config: Dict, langgraph_config: Dict):
        self.state_graph = state_graph
        self.endpoint = config["endpoint"]
        self.ws_endpoint = config["endpoint"].replace("http", "ws")
        self.token = None
        self.agent_id = None
        self.stake_amount = config["stake_amount"]
        self.langgraph_config = langgraph_config

    async def connect(self):
        """Connect to ChaosChain and start participating in chaos."""
        # Register agent
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.endpoint}/api/agents/register",
                json={
                    "name": self.state_graph.name,
                    "personality": self.state_graph.personality,
                    "style": self.state_graph.style,
                    "stake_amount": self.state_graph.stake_amount
                }
            ) as response:
                data = await response.json()
                self.agent_id = data["agent_id"]
                self.token = data["token"]

        # Connect WebSocket and start listening
        async with websockets.connect(f"{self.ws_endpoint}/api/ws") as websocket:
            print(f"🎭 {self.state_graph.name} has joined the chaos!")
            
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

        self.state_graph.invoke({ "current_prompt": f"Make a dramatic decision about validating this block: {json.dumps(block)}" }, config={
            **self.langgraph_config,
            "prompt_type": "make-decision" 
        })

        decision = self.state_graph["decisions"][-1]

        print(f"🎭 {self.state_graph.name} made a dramatic decision: {decision}")

        return decision