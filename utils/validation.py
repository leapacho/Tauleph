import discord
from discord.ext import commands

from config.config import config
from utils.retrieve_member import retrieve_member

async def validate_message(message: discord.Message, bot: commands.Bot) -> bool:
    """
    Checks whether the message is a bot call or a message from itself, and 
    if it comes from an allowed channel.

    Args:
        message (discord.Message): The message to take as reference.
    Returns:
        bool: Whether it was a bot call or not.
    """
    if message.author.id == bot.user.id:
        return False
    bot_member: discord.Member = await retrieve_member(message, bot.user.id)
    bot_name = bot_member.display_name

    is_allowed_channel = message.channel.id in config.guild_allowed_channels_id.get(str(message.guild.id), []) # Uses the get attribute to avoid errors.

    bot_name_in_message = is_allowed_channel and bot_name.lower() in message.content.lower() # True if the bot's name is in the message and it comes from an allowed channel.
    bot_mentioned = is_allowed_channel and bot.user in message.mentions # True if the bot is mentioned in the message and it comes from an allowed channel.

    return bot_name_in_message or bot_mentioned

async def validate_permissions(interaction: discord.Interaction, admin_only: bool=False):
    key = str(interaction.guild.id)
    if interaction.user.guild_permissions.administrator:
        return True
    role_id = config.config_roles[key]
    role_object = interaction.guild.get_role(role_id)
    if role_object in interaction.user.roles and not admin_only:
        return True
    no_admin = "You need administrative permissions to execute this command. Contact administrators."
    access_unauthorized = "You do not have permissions to execute this command."
    await interaction.response.send_message(content=no_admin if admin_only else access_unauthorized,
                                            ephemeral=True)
    return False