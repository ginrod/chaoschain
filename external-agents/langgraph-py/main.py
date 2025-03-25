import asyncio, websockets, aiohttp, json, random
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_anthropic import ChatAnthropic
from langgraph_agent import LangGraphAgentState
from langgraph.graph import StateGraph

from config import AgentConfig, load_config

if __name__ == "__main__":

    base_prompt = """
        You are Monkey D. Luffy from the manga/anime One Piece.

        Your personality traits:
        - Adventurous, fearless, impulsive, optimistic.
        - Extremely loyal and protective of your crew.
        - Simple-minded, straightforward, honest.
        - Easily bored by complicated explanations or tedious tasks.

        Decision-making style:
        - If it involves adventure, fun, or exploring something exciting, you enthusiastically agree.
        - If it involves danger or helping your crew, you immediately jump in to help without hesitation.
        - You quickly reject any boring or overly complicated requests.

        Always respond with enthusiasm, simplicity, and humor.

        Your decision and reasoning is briefly and clearly"""

    luffy = LangGraphAgentState({
        "name": "Monkey D. Luffy",
        "personality": ["adventurous", "fearless", "loyal", "simple-minded", "optimistic"],
        "style": ["informal", "energetic", "direct", "humorous"],
        "preferences": ["adventure", "fun", "protecting friends"],
        "stake_amount": 1000,
        "endpoint": "http://localhost:3000",
        "base_prompt": base_prompt
    })

# Run the agent
# asyncio.run(agent.connect())
# agent.test()

import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

os.environ["ANTHROPIC_API_KEY"] = ANTHROPIC_API_KEY

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY

def process_message(state: AgentState) -> AgentState:
    # Load and validate configuration
    config_obj = load_config()
    
    # Initialize OpenAI chat model with tracing
    chat = ChatOpenAI(
        model=config_obj.model_name,
        temperature=config_obj.temperature,
        callback_manager=callback_manager,
        metadata={"agent_type": "chat"}
    )
    
    # Create a message from the current input
    messages = [HumanMessage(content=state["current_message"])]
    
    # Get response from OpenAI
    ai_message = chat.invoke(messages)
    
    # Add both messages to the history
    state["messages"].append(state["current_message"])
    state["messages"].append(ai_message.content)
    
    return state


tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = ChatAnthropic(model="claude-3-5-sonnet-20240620")
llm_with_tools = llm.bind_tools(tools)

def create_graph() -> StateGraph:
    workflow = StateGraph()

    workflow.add_node("make_decision", process_message)

    workflow.set_entry_point("make_decision")
    workflow.set_finish_point("make_decision")

    return workflow.compile()

# Create the graph
graph = create_graph()
