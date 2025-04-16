from langchain_google_genai import ChatGoogleGenerativeAI
#from langchain_groq import ChatGroq
from langchain_core.messages import AIMessage
from typing import Annotated, Union
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.graph import CompiledGraph
from langgraph.graph.message import add_messages 
from langchain_community.utilities import SearxSearchWrapper
from langchain_community.tools.searx_search.tool import SearxSearchResults
from langgraph.prebuilt import ToolNode, tools_condition
from textwrap import TextWrapper
#import sqlite3
#from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
from utils.split_chunks import split_text

load_dotenv() #Loads environment variables.

# conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
memory = MemorySaver() #SqliteSaver is a class that intefaces sqlite3.
searx_search = SearxSearchWrapper(searx_host="http://localhost:32787") #SearxSearchWrapper is a class that allows you to interact with the Searx API.
searx_tool = SearxSearchResults(wrapper=searx_search, num_results=10) #SearxSearchResults is a class that allows you to get search results from Searx.

class State(TypedDict): 
    messages: Annotated[list, add_messages] #Creates the state. The state is a dictionary that contains the messages.

def setup_graph(input_model: str) -> CompiledGraph:
    graph_builder = StateGraph(State) #StateGraph is a class that creates a graph with the state.

    llm = ChatGoogleGenerativeAI(model=input_model)
    tools = [searx_tool]
     
    llm_with_tools = llm.bind_tools(tools)

    def chatbot(state: State) -> dict:
        response = {"messages": [llm_with_tools.invoke(state["messages"])]}

        chunked_lines=split_text(response["messages"][-1].content, 2000)
       
        response["messages"][-1].content = chunked_lines
        
        return response
    
    def chatbot_mock(state: State) -> dict:
        return{"messages": "This is a mock test of the chatbot."}
    
    def chatbot_mock_char_limit(state: State) -> dict:
        return{"messages": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}

    def split_text_into_chunks(state: State, chunk_size: int = 2000) -> State:
        w = TextWrapper(width=chunk_size,break_long_words=True,replace_whitespace=False)
        chunked_lines=w.wrap(state["messages"][-1].content[-1])
        state["messages"][-1] = AIMessage(content=chunked_lines)
        return state

    graph_builder.add_node("chatbot", chatbot) #Adds the chatbot node to the graph.
    graph_builder.add_node("tools", ToolNode(tools)) #Adds the tools node to the graph.
    graph_builder.add_conditional_edges("chatbot", tools_condition) #Adds conditional edges between the chatbot and tools nodes.
    graph_builder.add_edge("tools", "chatbot") #Adds an edge between the tools and chatbot nodes.
    graph_builder.set_entry_point("chatbot") #Sets the entry point of the graph to the chatbot node.
    runnable = graph_builder.compile(checkpointer=memory) #Compiles the graph with the memory checkpointer.

    return runnable #Returns the runnable graph.

async def run_graph(graph: CompiledGraph, config, initial_messages=None) -> str:
    """
    Processes the input messages through the graph and returns the last message.
    """

    response = await graph.ainvoke({"messages": initial_messages}, config) if initial_messages else await graph.ainvoke(None, config) 

    # if response["messages"][-1].content > 2000:
    #     response = split_text(response["messages"][-1].content)

    return response["messages"][-1].content



