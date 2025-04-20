from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph.graph import CompiledGraph
from typing import AsyncIterator
from langgraph.types import StateSnapshot


async def config_history(graph: CompiledGraph, config: dict) -> dict:
    """
    Returns the last config in the state if it isn't an AIMessage.   
    """
    state_history: AsyncIterator[StateSnapshot] = graph.aget_state_history(config)
    configs=[]

    async for state in state_history:
        messages = state.values.get("messages", []) #Gets the messages in the state.
        if messages:
            last_message=messages[-1] #Gets the last message in the messages.
        else:
            break
        if not isinstance(last_message, AIMessage): #Checks if the last message is not an AIMessage.
            configs.append(state.config) #Appends the config to the configs list.
    return configs[0]

async def ai_config_history(graph: CompiledGraph, config: dict) -> list:
    """
    Returns the first configs in the state that have an AIMessage.
    """
    state_history: AsyncIterator[StateSnapshot] = graph.aget_state_history(config)
    configs_unreversed=[]
    
    async for state in state_history:
        messages = state.values.get("messages", [])
        if messages:
            last_message=messages[-1] #Gets the last message in the messages.
        else:
            break
        if isinstance(last_message, ToolMessage): #Ignores the tool messages.
            continue
        if isinstance(last_message, AIMessage) and last_message.content: #Checks if the last message is an AIMessage and if it has content (a string).
            configs_unreversed.append(state.config) #Appends the config to the configs_unreversed list.
        else:
            break
        configs = list(reversed(configs_unreversed)) #Reverses the list of configs.
    return configs