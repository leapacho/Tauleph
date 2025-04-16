from message_processor import MessageProcessor
from checkpoint_manager import CheckpointManager
from discord_ui_handler import discord_ui_handler, RegenButtons


checkpoint_manager = CheckpointManager()


async def entry_point():
    """
    Entry point for processing messages.
    
    This function is called to start the message processing flow.
    """

    # Process the message.
    discord_ui_handler.regen_buttons = RegenButtons()
    await discord_ui_handler._prepare_new_responses()
    
    
    message_processor = MessageProcessor()
    result = await message_processor.process_message()

    # Get the API response.
    llm_output = await checkpoint_manager.response(result[0], result[1])

    await discord_ui_handler.send_message(llm_output)


    