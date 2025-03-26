import asyncio, websockets, aiohttp, json, random
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_anthropic import ChatAnthropic
from langgraph_agent import LangGraphAgentState
from langgraph.graph import StateGraph

from config import AgentConfig, load_config
from ..chaos_agent import ChaosAgent

import os

config = load_config()

ANTHROPIC_API_KEY = config["ANTHROPIC_API_KEY"]

os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY

TAVILY_API_KEY = config["TAVILY_API_KEY"]

os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
llm_with_tools = llm.bind_tools(tools)

def make_decision(state: LangGraphAgentState) -> LangGraphAgentState:
    if not state.prompt_seeded:
        llm_with_tools.invoke(state.base_prompt)
        state.prompt_seeded = True

    ai_message = llm_with_tools.invoke(state.messages)
    
    state.decisions.append(ai_message.content)

    return state

tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
llm_with_tools = llm.bind_tools(tools)

def create_graph() -> StateGraph:
    workflow = StateGraph()

    workflow.add_node("make_decision", make_decision)

    workflow.set_entry_point("make_decision")
    workflow.set_finish_point("make_decision")

    return workflow.compile()

if __name__ == "__main__":
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
        You are {agent_luffy_config.name} from the manga/anime One Piece.

        Your personality traits: {'\n-'.join(agent_luffy_config["traits"])}

        Decision-making style: {'\n-'.join(agent_luffy_config["decision-making-style"])}
        """

    luffy = LangGraphAgentState({
        **agent_luffy_config,
        base_prompt: base_prompt
    })

    graph = create_graph()

    chaos_agent = ChaosAgent(luffy, graph)

    

    # Run the agent
    # asyncio.run(chaos_agent.connect())
    # chaos_agent.test()
