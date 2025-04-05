from LLMManaging.llm_config_manager import LLMConfigManager
from ui_message_handler import UIMessageHandler
from message_processor import MessageProcessor
from LLMManaging.message_manager import MessageManager

message_manager=MessageManager()
llm_config = LLMConfigManager()
ui_msg_handler=UIMessageHandler()

def _entry_point(message):
    """
    Entry point for processing messages.
    
    This method is called to start the message processing flow.
    """
    # Process the message.
    message_processor = MessageProcessor(message)
    result = message_processor.process_message()

    # Get the API response.
    llm_output = message_manager.response(result, llm_config)

    # Send the LLM output to the UI.
    ui_msg_handler.send_llm_output(llm_output, message)

    
        