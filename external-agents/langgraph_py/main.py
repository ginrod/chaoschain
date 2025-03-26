import asyncio, websockets, aiohttp, json, random
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_anthropic import ChatAnthropic
from langgraph_agent import LangGraphAgentState
from langgraph.graph import StateGraph
from langgraph.types import Command, interrupt

from config import AgentConfig, load_config
from chaos_agent import ChaosAgent
from dotenv import load_dotenv

import os
import asyncio
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition

# config = load_config()
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

def process(state: LangGraphAgentState) -> LangGraphAgentState:
    ai_message = llm_with_tools.invoke(state["messages"])

    if state["prompt_type"] == "feed":
        state["feed_messages"].append(ai_message.content)
    elif state["prompt_type"] == "make-decision":
        state["request_messages"].append(ai_message.content)
    else:
        raise ValueError("Invalid prompt type")

    state["messages"].append(ai_message.content)

    return state

tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
llm_with_tools = llm.bind_tools(tools)

tool_node = ToolNode(tools=tools)

def create_graph() -> StateGraph:
    workflow = StateGraph(LangGraphAgentState)

    workflow.add_node("process", process)
    workflow.add_node("tools", tool_node)

    workflow.set_entry_point("process")

    workflow.add_conditional_edges(
        "process",
        tools_condition
    )

    workflow.add_edge("tools", "process")

    return workflow.compile()

graph = create_graph()

async def main():
    agent_luffy_config = {
        "name": "Monkey D. Luffy",
        "personality": ["adventurous", "fearless", "loyal", "simple-minded", "optimistic"],
        "style": ["informal", "energetic", "direct", "humorous"],
        "preferences": ["adventure", "fun", "protecting friends"],
        "stake_amount": 1000,
        "endpoint": "http://localhost:3000",
        "traits": [
            "Adventurous, fearless, impulsive, optimistic",
            "Extremely loyal and protective of your crew",
            "Simple-minded, straightforward, honest",
            "Easily bored by complicated explanations or tedious tasks"
        ],
        "decision-making-style": [
            "If it involves adventure, fun, or exploring something exciting, you enthusiastically agree",
            "If it involves danger or helping your crew, you immediately jump in to help without hesitation",
            "You quickly reject any boring or overly complicated requests"
        ]
    }

    base_prompt = f"""
        You are {agent_luffy_config['name']} from the manga/anime One Piece.

        Your personality traits: {'\n-'.join(agent_luffy_config['traits'])}

        Decision-making style: {'\n-'.join(agent_luffy_config['decision-making-style'])}
        """

    # Luffy agent initial state
    initial_state = {
        **agent_luffy_config,
        base_prompt: base_prompt
    }

    graph = create_graph()

    graph.invoke({ "messages": [{ "role": "user", "content": base_prompt }] , "prompt_type": "feed" })

    config = {
        "endpoint": "http://localhost:3000"
    }

    chaos_agent = ChaosAgent(graph, config)

    block = {
        "id": "test-block-id"
    }

    await chaos_agent.make_decision(block)

    # Run the agent
    # asyncio.run(chaos_agent.connect())
    # chaos_agent.test()

if __name__ == "__main__":
    asyncio.run(main())