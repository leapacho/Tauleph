import discord
import os

from discord.ext import commands
from dotenv import load_dotenv
from discord_obj_processor import discord_obj
from entry_point import entry_point
from utils.validation import validate_message
from config import config

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
    await config.set_guild_vars_default(guild)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')

    await bot.load_extension("cmds.help_commands")
    await bot.load_extension("cogs.model_select")
    await bot.load_extension("cogs.sys_prompts")
    await bot.load_extension("cogs.channel_permissions")
    await bot.load_extension("cogs.set_guild_defaults")

    await bot.tree.sync()   

@bot.event
async def on_message(message: discord.Message):
    await discord_obj.update_object_variables(message, bot)
    if not await validate_message(message):
        return
    await entry_point()

bot.run(os.environ.get("BOT_API_KEY"))