import discord
from discord.ext import commands
from dotenv import load_dotenv
from discord_obj_processor import discord_obj_processor
from entry_point import entry_point
import os

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} - {bot.user.id}')
    print('------')

@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    await discord_obj_processor.update_object_variables(message, bot)
    await message.channel.send(await entry_point())

bot.run(os.environ.get("BOT_API_KEY"))