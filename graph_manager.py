from langchain_core.messages import AIMessage, ToolMessage
from langgraph.graph.graph import CompiledGraph

class GraphManager:
    def __init__(self, graph: CompiledGraph, config):
        self.config = config
        self.graph = graph
    
    def _config_history(self):
        """
        Returns the last config in the state if it isn't an AIMessage.   
        """
        state_history=self.graph.get_state_history(self.config)
        configs=[]

        for state in state_history:
            messages = state.values.get("messages", []) #Gets the messages in the state.
            if messages:
                last_message=messages[-1] #Gets the last message in the messages.
            else:
                break
            if not isinstance(last_message, AIMessage): #Checks if the last message is not an AIMessage.
                configs.append(state.config) #Appends the config to the configs list.
        return configs[0]

    def _ai_config_history(self):
        """
        Returns the first configs in the state that have an AIMessage.
        """
        state_history=self.graph.get_state_history(self.config)
        configs_unreversed=[]
        for state in state_history:
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
