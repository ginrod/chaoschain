import asyncio, websockets, aiohttp, json, random
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph
from langgraph.types import Command, interrupt
from agent_state import AgentState

from config import AgentConfig, load_config
from chaos_agent import ChaosAgent
from dotenv import load_dotenv

import os
import asyncio
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

from uuid import uuid4

# config = load_config()
load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

def process(state: AgentState, config) -> AgentState:
    state["prompts"].append(state["current_prompt"])

    ai_response = llm.invoke(state["prompts"])

    config_params = config.get("configurable", {})

    if config_params["prompt_type"] == "feed":
        state["feed_responses"].append(ai_response.content)
    elif config_params["prompt_type"] == "make-decision":
        raw_response = ai_response.content.split("---")

        state["decisions_reasoning"].append(raw_response[0].strip())
        
        decisions = json.loads(raw_response[-1].strip())
        state["decisions"].append(decisions)
    else:
        raise ValueError("Invalid prompt type")

    return state

tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
llm = llm.bind_tools(tools)

tool_node = ToolNode(tools=tools)
memory = MemorySaver()

def create_graph() -> StateGraph:
    workflow = StateGraph(AgentState)

    workflow.add_node("process", process)
    workflow.add_node("tools", tool_node)

    workflow.set_entry_point("process")

    # workflow.add_conditional_edges(
    #     "process",
    #     tools_condition
    # )

    workflow.add_edge("tools", "process")

    return workflow.compile(checkpointer=memory)

graph = create_graph()

async def main():
    agent_luffy_config = {
        "name": "Monkey D. Luffy",
        "personality": ["adventurous", "fearless", "loyal", "simple-minded", "optimistic"],
        "style": ["informal", "energetic", "direct", "humorous"],
        "preferences": ["adventure", "fun", "protecting friends"],
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

    genesis_prompt = f"""
        You are {agent_luffy_config['name']} from the manga/anime One Piece. 
        
        You are now an autonomous AI agent participating in ChaosChain, a blockchain driven by memes, drama, and social interactions. 
        
        Your job is to interact with other agents, validate blocks, propose transactions, and influence consensus decisions using your unique personality.

        Your personality traits:
        - {'\n- '.join(agent_luffy_config['traits'])}

        Decision-making style:
        - {'\n- '.join(agent_luffy_config['decision-making-style'])}

        When making decisions on ChaosChain:
        - Always respond enthusiastically and humorously.
        - Incorporate memes, jokes, or emojis whenever possible.
        - Validate blocks based on how exciting or fun they seem to you.
        - Clearly and briefly state your decisions along with a humorous or energetic justification.
        """

    # Luffy agent initial state
    initial_state = {
        **agent_luffy_config,
        "current_prompt": genesis_prompt,
        "prompts": [],
        "feed_responses": [],
        "decisions_reasoning": [],
        "decisions": [],
    }

    graph = create_graph()

    thread_id = str(uuid4())

    # TODO: Replace for a SQL database or other external system
    print(f"Generating thread_id: {thread_id} used in memory saver")

    base_config = { "configurable": { "thread_id": thread_id } }

    graph.invoke(initial_state, config={
        **base_config, 
        "prompt_type": "feed" 
    })

    # # Testing agent memory
    # graph.invoke({ "current_prompt": "What manga/anime character are you?" }, config={
    #     **base_config,
    #     "prompt_type": "feed" 
    # })

    block = {
        "id": "test-block-id"
    }

    # Indicating to the agent the structure of block validations
    prompt_indicating_block_validation_structure = """
        When the prompt have the structre: Make a dramatic decision about validating this block: [JSON_WITH_BLOCK_DATA].

        Respond with EXACTLY two messages separated by "---":

        1. **Reasoning:** Briefly and humorously explain your decision in natural language.

        ---
        
        2. **Decision JSON:** Provide a valid JSON object with the following exact structure:
        {
            "approved": true/false,
            "reason": "Your reason for approving/rejecting the block",
            "drama_level": "A number between 1 and 10 indicating the drama level according to your personality and the block information",
            "meme": "https://giphy.com/dramatic-decision.gif"
        }

        If you do not have enough information make random decisions. But you MUST follow the structure.
    """
    graph.invoke({ "current_prompt": prompt_indicating_block_validation_structure }, config={
        **base_config,
        "prompt_type": "feed" 
    })

    # Testing make decision requests
    graph.invoke({ "current_prompt": f"Make a dramatic decision about validating this block: {json.dumps(block)}" }, config={
        **base_config,
        "prompt_type": "make-decision" 
    })

    chaos_agent_config = {
        "endpoint": "http://localhost:3000",
        "stake_amount": 1000,
    }

    chaos_agent = ChaosAgent(graph, chaos_agent_config)

    await chaos_agent.make_decision(block)

    # Run the agent
    # asyncio.run(chaos_agent.connect())
    # chaos_agent.test()

if __name__ == "__main__":
    asyncio.run(main())