import discord
from discord.ext import commands

class DiscordObjectProcessor:
    def __init__(self):
        self.message_author: str = ""
        self.bot_name: str = ""
        self.bot_user: discord.User = None
        self.message_content: str = ""
        self.bot_member: discord.Member = None
        self.text_channel: discord.TextChannel = None


        self.message: discord.Message = None
        self.guild: discord.Guild = None

        self.attachments: discord.Message = ""
        self.att_type: str = ""
        self.att_url: str = ""
        self.is_interaction: bool = False

    async def update_object_variables(self, discord_object: discord.Message, bot: commands.Bot):
        """
        Stores every needed variable from the discord object.

        Args:
            discord_object (Union[discord.Interaction, discord.Message]): The Discord object to take as reference.
            bot (commands.Bot): The bot instance.
            is_interaction (bool): Whether to process the message as an interaction or not (unused).
        """


        # if not self.is_interaction:
        self.guild = discord_object.guild
        self.message_author = discord_object.author.display_name 
        self.bot_user = bot.user
        self.bot_member = await self.guild.fetch_member(bot.user.id)
        self.bot_name = self.bot_member.display_name
        self.message_content = discord_object.content

        self.message = discord_object
        self.text_channel = self.message.channel
        
        self.attachments = discord_object.attachments
        self.att_type = self.attachments[-1].content_type if self.attachments else ""
        self.att_url = self.attachments[-1].url if self.attachments else ""
        # else:
        #     self.guild = discord_object.guild
        #     self.message_author = discord_object.user.display_name 
        #     self.bot_user = bot.user
        #     self.bot_member = await self.guild.fetch_member(bot.user.id)
        #     self.bot_name = self.bot_member.display_name
        #     self.message_content = discord_object.content

        #     self.message = discord_object.message
        #     self.text_channel = self.message.channel

discord_obj = DiscordObjectProcessor()

