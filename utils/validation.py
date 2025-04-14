from discord_obj_processor import discord_obj_processor
import discord

async def validate_message(message: discord.Message) -> bool:
    """
    Checks whether the message is a bot call or a message from itself, and 
    if it comes from an allowed channel.

    Args:
        message (discord.Message): The message to take as reference.
    Returns:
        bool: Whether it was a bot call or not.
    """
    if message.author.id == discord_obj_processor.bot_user.id:
        return False

    #is_allowed_channel = message.channel.id in llm_config.allowed_channels[str(message.guild.id)]

    bot_name_in_message = discord_obj_processor.bot_name.lower() in message.content.lower() # True if the bot's name is in the message and it comes from an allowed channel.
    bot_mentioned = discord_obj_processor.bot_user in message.mentions # True if the bot is mentioned in the message and it comes from an allowed channel.

    return bot_name_in_message or bot_mentioned