from langchain_core.messages import HumanMessage, SystemMessage
from graph import run_graph, run_graph_mock, setup_graph

class CheckpointManager:
    def __init__(self):
        self.graph = setup_graph("gemini-2.0-flash")
        self.default_config = {"configurable": {"thread_id": "1"}}

    async def response(self, user_input=None, system_input=None):
        """
        Invokes the LLM for a response.
        """

        #Prepare initial messages.
        user_message = HumanMessage(
            content=user_input
        )
        system_message = SystemMessage(
            content=system_input
        )
        initial_messages = [user_message, system_message]
        #Process input.
        response = await run_graph(self.graph, self.default_config, initial_messages)
        self.current_index=0 #Resets all the indices.
        self.ai_configs = []
        return response