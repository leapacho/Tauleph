import discord
import os

from discord.ext import commands
from dotenv import load_dotenv
from entry_point import entry_point
from utils.validation import validate_message
from config.config import config

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="", intents=intents, help_command=None)

@bot.event
async def on_guild_join(guild: discord.Guild):
    """
    Sends a message to the guild when the bot joins it.

    See Discord.py's API reference for more details on this method.
    """
    guild_channels=guild.text_channels
    for channel in guild_channels:
        try:
            await channel.send("This is Tauleph, a simple AI chatbot. To get started, say Tauleph's name in this channel or use the commands /help quickstart or /help commands.")
            await config.allow_channel(channel)
            return
        except discord.Forbidden: # discord.Forbidden is an exception. It's raised when the bot tries to send a message to a channel
            continue              # it isn't allowed to send messages in.
@bot.event
async def on_guild_remove(guild: discord.Guild):
    await config.delete_guild_vars(guild)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')

    await bot.load_extension("bot.cmds.help_commands")
    await bot.load_extension("bot.cogs.model_select")
    await bot.load_extension("bot.cogs.sys_prompts")
    await bot.load_extension("bot.cogs.channel_permissions")
    await bot.load_extension("bot.cogs.set_guild_defaults")
    await bot.load_extension("bot.cogs.config_permissions")

    await bot.tree.sync()   

@bot.event
async def on_message(message: discord.Message):
    if not await validate_message(message, bot):
        return
    await entry_point(message, bot)

bot.run(os.environ.get("BOT_API_KEY"))