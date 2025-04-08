from message_processor import MessageProcessor
from checkpoint_manager import CheckpointManager



checkpoint_manager = CheckpointManager()

async def entry_point():
    """
    Entry point for processing messages.
    
    This function is called to start the message processing flow.
    """
    # Process the message.
    message_processor = MessageProcessor()
    result = await message_processor.process_message()

    # Get the API response.
    llm_output = await checkpoint_manager.response(result[0], result[1])

    return llm_output


    