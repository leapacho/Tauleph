import discord
from llm_graph.message_processor import MessageProcessor
from llm_graph.checkpoint_manager import checkpoint_manager
from bot.discord_ui_handler import discord_ui_handler, RegenButtons
from discord.ext import commands
from config.config import config



async def entry_point(message: discord.Message, bot: commands.Bot):
    """
    Entry point for processing messages.
    
    This function is called to start the message processing flow.
    """

    # Initiate variables.
    discord_ui_handler.regen_buttons = RegenButtons()
    
    # Process the message.
    message_processor = MessageProcessor(message, bot)
    result = await message_processor.process_message()
    # Get the API response.
    
    llm_output = await checkpoint_manager.response(result[0], result[1], message)

    await discord_ui_handler.send_message(llm_output, message.channel)


    