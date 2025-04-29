from langchain_google_genai import ChatGoogleGenerativeAI
from google.api_core.exceptions import GoogleAPIError
from langchain_core.messages import AIMessage
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.graph import CompiledGraph
from langgraph.graph.message import add_messages 
from langchain_community.utilities import SearxSearchWrapper
from langchain_community.tools.searx_search.tool import SearxSearchResults
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import trim_messages
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
from utils.split_chunks import split_text
import asyncio
load_dotenv() #Loads environment variables.
searx_search = SearxSearchWrapper(searx_host="http://localhost:32787") #SearxSearchWrapper is a class that allows you to interact with the Searx API.
searx_tool = SearxSearchResults(wrapper=searx_search, num_results=10) #SearxSearchResults is a class that allows you to get search results from Searx.

class State(TypedDict): 
    messages: Annotated[list, add_messages] #Creates the state. The state is a dictionary that contains the messages.

class Graph:
    def __init__(self):
        self.token_count: int = 500000
        self.memory = None

    def message_trimming(self, state: State, llm: ChatGoogleGenerativeAI):
        trimmed_messages = trim_messages(
            state["messages"],
            strategy="last",
            token_counter=llm,
            max_tokens=self.token_count,
            start_on="human",
            end_on=("human", "system", "tool"),
            include_system=True,
            )
        
        state["messages"] = trimmed_messages

        return state["messages"]

    async def clear_history(self, thread_id: str):
        """
        Clears the chat history for a specific thread ID using the checkpointer.
        This should be called from your Discord bot code when the clear command is issued.
        """
        print(type(thread_id))
        try:
            await self.memory.adelete_thread(thread_id=thread_id)
            print(f"History cleared for thread: {thread_id}")
        except Exception as e:
            print(f"Error clearing history for thread {thread_id}: {e}")


    async def setup_graph(self, input_model: str) -> CompiledGraph:
        graph_builder = StateGraph(State) #StateGraph is a class that creates a graph with the state.

        llm = ChatGoogleGenerativeAI(model=input_model,
                                    max_retries=6,
                                    timeout=2)
        tools = [searx_tool]
        
        llm_with_tools = llm.bind_tools(tools)

        def chatbot(state: State) -> dict:
            #Trimming message history.
            trimmed_messages = self.message_trimming(state, llm)

            #LLM calling.
            response = {"messages": [llm_with_tools.invoke(trimmed_messages)]}

            #Splitting text into lists of 2000 characters.
            chunked_lines=split_text(response["messages"][-1].content, 2000)
            response["messages"][-1].content = chunked_lines

            return response
        
        def chatbot_mock(state: State) -> dict:
            response = {"messages": "This is a mock test of the chatbot."}
            chunked_lines=split_text(response["messages"], 2000)
            response["messages"] = AIMessage(content=chunked_lines)
            return response
        
        def chatbot_mock_char_limit(state: State) -> dict:
            response = {"messages": "a" * 2001}
            print(response)
            chunked_lines=split_text(response["messages"], 2000)
            response["messages"] = AIMessage(content=chunked_lines)
            return response

        graph_builder.add_node("chatbot", chatbot) #Adds the chatbot node to the graph.
        graph_builder.add_node("tools", ToolNode(tools)) #Adds the tools node to the graph.
        graph_builder.add_conditional_edges("chatbot", tools_condition) #Adds conditional edges between the chatbot and tools nodes.
        graph_builder.add_edge("tools", "chatbot") #Adds an edge between the tools and chatbot nodes.
        graph_builder.set_entry_point("chatbot") #Sets the entry point of the graph to the chatbot node.
        
        return graph_builder #Returns the graph builder.

    async def run_graph(self, graph_builder: StateGraph, config, initial_messages=None) -> str:
        """
        Processes the input messages through the graph and returns the last message.
        """
        # Accesses the Sqlite database asynchronously. 
        async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as memory:
            graph = graph_builder.compile(checkpointer=memory) #Compiles the graph with the memory checkpointer.
            self.memory = memory

            try:
                response = await graph.ainvoke({"messages": initial_messages}, config) if initial_messages else await graph.ainvoke(None, config) 
            except GoogleAPIError as e:
                response = f"Error: \n\n{e}\n\nContact Discord user 'limonero.' or start an issue on Tauleph's GitHub page if this is a recurring error."
                return [response]
            return response["messages"][-1].content

graph = Graph()
