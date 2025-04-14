import discord
import os

from discord.ext import commands
from dotenv import load_dotenv
from discord_obj_processor import discord_obj_processor
from entry_point import entry_point
from utils.validation import validate_message


load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')

    await bot.load_extension("cmds.help_commands")
    await bot.load_extension("cogs.model_select")

    await bot.tree.sync()

@bot.event
async def on_message(message: discord.Message):
    await discord_obj_processor.update_object_variables(message, bot)
    if not await validate_message(message):
        return
    llm_message = await entry_point()
    for chunk in llm_message: await message.channel.send(chunk)

bot.run(os.environ.get("BOT_API_KEY"))