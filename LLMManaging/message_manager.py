from LLMManaging.google_exception_handler import GoogleAPIExceptionHandler
from LLMManaging.graph_manager import config, memory, process_input, setup_graph


from google.genai.errors import APIError
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage


class MessageManager: #finish integrating Gemini's mulimodality
    """
    Manages all the messages sent and returns the responses.

    Includes managing navigation (paginations).
    """
    def __init__(self):

        self.ai_configs = []
        self.current_index = 0
        global config
        self.model = ""
        self.graph = setup_graph(self.model)

    def _prepare_processing(self, initial_messages=None):
        #Choose the config based on the initial_messages and current config.
        if not initial_messages:
            cfg = self._config_history()
        elif self.current_config is not None:
            cfg = self.current_config
        else:
            cfg = config

        try:
            return process_input(self.graph, cfg, initial_messages=initial_messages)
        except APIError as err:
            exception_handler = GoogleAPIExceptionHandler(err, self.graph, cfg, initial_messages)
            return exception_handler.handle_api_exception()


    def refresh_model(self, model: str):
        """
        Updates the model.
        """
        self.model = model
        self.graph = setup_graph(self.model)

    def _config_history(self):
        """
        Returns the last config in the state if it isn't an AIMessage.   
        """
        state_history=self.graph.get_state_history(config)
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
        Returns a list of configs that are AIMessages.
        """
        state_history=self.graph.get_state_history(config)
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
        self.ai_configs = configs

    def response(self, user_input=None, system_input=None):
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
        response = self._prepare_processing(initial_messages)
        self.current_index=0 #Resets all the indices.
        self.ai_configs = []
        return response

    def regenerate(self): 
        response = self._prepare_processing()
        self._ai_config_history() #Updates indices.
        self.current_index=len(self.ai_configs)-1 #Sets the current index to the last index.
        return response

    def navigate_forward(self):
        self._ai_config_history()
        self.current_index+=1
        msg = memory.get(self.current_config)["channel_values"]["messages"][-1].content
        return msg

    def navigate_backward(self):
        self._ai_config_history()
        self.current_index-=1
        msg = memory.get(self.current_config)["channel_values"]["messages"][-1].content
        return msg

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


    def update_thread_id(self, thread_id: int):
        """
        Updates the thread ID with the provided one.
        """
        config["configurable"]["thread_id"]=thread_id #Accesses the configurable key in the config dictionary and sets the thread_id to the provided one.
        if self.current_config: #If there is a current config...
            self.current_config["configurable"]["thread_id"]=thread_id #...sets the thread_id in the current config to the provided one.