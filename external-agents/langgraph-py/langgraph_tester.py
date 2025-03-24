from langgraph_agent import LangGraphAgent

if __name__ == "__main__":
    # Example usage

    agent = LangGraphAgent({
        "name": "ChaosOracle",
        "personality": ["mystical", "dramatic", "unpredictable"],
        "style": "Speaks in riddles and emojis",
        "stake_amount": 1000,
        "endpoint": "http://localhost:3000"
    })

# Run the agent
# asyncio.run(agent.connect())

# agent.test()