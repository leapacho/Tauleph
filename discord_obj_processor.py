import discord
from discord.ext import commands

class DiscordObjectProcessor:
    def __init__(self):
        self.message_author: str = ""
        self.bot_name: str = ""
        self.bot_user: discord.User = None
        self.message_content: str = ""

        self.message: discord.Message = None
        self.guild: discord.Guild = None

        self.attachments: discord.Message = ""
        self.att_type: str = ""
        self.att_url: str = ""

    async def update_object_variables(self, discord_object: discord.Message, bot: commands.Bot):
        """
        Gets a list of names that contains the bot's name, the user's name, and the user's message.

        Args:
            discord_object (discord.Message/Interaction): The Discord object to take as reference.
            is_interaction (bool): 
        """
        
        self.guild = discord_object.guild
        self.message_author = discord_object.author.display_name 
        self.bot_user = bot.user
        bot_member = await self.guild.fetch_member(bot.user.id)
        self.bot_name = bot_member.display_name
        self.message_content = discord_object.content
        
        
        self.message = discord_object
        
        self.attachments = discord_object.attachments
        self.att_type = self.attachments[-1].content_type if self.attachments else ""
        self.att_url = self.attachments[-1].url if self.attachments else ""
        
discord_obj_processor = DiscordObjectProcessor()

