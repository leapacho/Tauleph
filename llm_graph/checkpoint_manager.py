from langchain_core.messages import HumanMessage, SystemMessage
from llm_graph.graph import graph
from llm_graph.graph_manager import config_history, ai_config_history
from config.config import config



class CheckpointManager:
    def __init__(self):
        self.default_config = {"configurable": {"thread_id": "1"}}
        self.current_index = 0
        self.ai_configs = []
        


    async def response(self, user_input=None, system_input=None):
        """
        Invokes the LLM for a response.
        """
        self.graph = graph.setup_graph(await config.current_model())

        #Prepare initial messages.
        user_message = HumanMessage(
            content=user_input
        )
        system_message = SystemMessage(
            content=system_input
        )
        initial_messages = [user_message, system_message]
        #Process input.
        response = await graph.run_graph(self.graph, self.default_config, initial_messages)
        self.current_index=0 #Resets all the indices.
        self.ai_configs = []
        return response
    
    async def regeneration(self):
        """
        Invokes the LLM for a regeneration.
        """
        self.graph = graph.setup_graph(await config.current_model())
        new_config = await config_history(self.graph, self.default_config)
        response = await graph.run_graph(self.graph, new_config)
        self.ai_configs = await ai_config_history(self.graph, self.default_config) 
        self.current_index = len(self.ai_configs)-1
        return response
    
    async def page_backwards(self):
        self.current_index-=1
        msg = (await graph.memory.aget(self.current_config))["channel_values"]["messages"][-1].content
        return msg
    
    async def page_forwards(self):
        self.current_index+=1
        msg = (await graph.memory.aget(self.current_config))["channel_values"]["messages"][-1].content
        return msg
    
    async def update_thread_id(self, thread_id: str) -> None:
        """
        Updates the thread ID with the provided one.
        """
        self.default_config["configurable"]["thread_id"]=thread_id #Accesses the configurable key in the config dictionary and sets the thread_id to the provided one.
        if self.current_config: #If there is a current config...
            self.current_config["configurable"]["thread_id"]=thread_id #...sets the thread_id in the current config to the provided one.

    @property
    def current_config(self):
        if 0 <= self.current_index < len(self.ai_configs):
            return self.ai_configs[self.current_index]
        return None

    @property
    def can_go_backward(self):
        return self.current_index - 1 < 0 #Returns True if current_index is lower than 0, and viceversa 

    @property
    def can_go_forward(self):
        return self.current_index + 1 > len(self.ai_configs) - 1 #Returns True if current_index is higher than the current number of indices, and viceversa 

    @property
    def indices(self):
        return f"{self.current_index+1}/{len(self.ai_configs)}"

checkpoint_manager = CheckpointManager()

