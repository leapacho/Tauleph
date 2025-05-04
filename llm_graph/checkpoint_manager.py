from langchain_core.messages import HumanMessage, SystemMessage
from llm_graph.graph import graph
from llm_graph.graph_manager import config_history, ai_config_history
from config.config import config
import discord


class CheckpointManager:
    def __init__(self):
        self.current_index = 0
        self.ai_configs = []
        self.guild: discord.Guild = None
        
    async def response(self, user_input: str, system_input: str, message: discord.Message):
        """
        Invokes the LLM for a response.
        """
        compiled_graph = graph.setup_graph(await config.current_model(message.guild))

        #Prepare initial messages.
        user_message = HumanMessage(
            content=user_input
        )
        system_message = SystemMessage(
            content=system_input
        )
        initial_messages = [user_message, system_message]
        #Process input.
        graph_config = config.get_graph_config(message)
        response = await graph.run_graph(compiled_graph, graph_config, initial_messages)
        self.current_index=0 #Resets all the indices.
        self.ai_configs = []
        return response
    
    async def regeneration(self, interaction: discord.Interaction):
        """
        Invokes the LLM for a regeneration.
        """
        graph_config = config.get_graph_config(interaction)
        compiled_graph = graph.setup_graph(await config.current_model(interaction.guild))
        new_config = await config_history(compiled_graph, graph_config)
        response = await graph.run_graph(compiled_graph, new_config)
        self.ai_configs = await ai_config_history(compiled_graph, graph_config) 
        self.current_index = len(self.ai_configs)-1
        return response
    
    async def page_backward(self):
        if not self.can_go_backward:
            self.current_index-=1
            msg = (await graph.memory.aget(self.current_config))["channel_values"]["messages"][-1].content
            return msg
        return ["None."]
    
    async def page_forward(self):
        if not self.can_go_forward:
            self.current_index+=1
            msg = (await graph.memory.aget(self.current_config))["channel_values"]["messages"][-1].content
            return msg
        return ["None."]

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

