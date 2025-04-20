from message_processor import MessageProcessor
from checkpoint_manager import checkpoint_manager
from discord_ui_handler import discord_ui_handler, RegenButtons
from discord_obj_processor import discord_obj





async def entry_point():
    """
    Entry point for processing messages.
    
    This function is called to start the message processing flow.
    """

    # Initiate variables.
    discord_ui_handler.regen_buttons = RegenButtons()
    await checkpoint_manager.update_thread_id(f"{discord_obj.guild.id}")
    
    
    # Process the message.
    message_processor = MessageProcessor()
    result = await message_processor.process_message()
    # Get the API response.
    llm_output = await checkpoint_manager.response(result[0], result[1])

    await discord_ui_handler.send_message(llm_output)


    