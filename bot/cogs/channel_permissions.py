import discord
from discord.ext import commands
from discord import app_commands

from config.config import config
from bot.discord_obj_processor import discord_obj
from utils.validation import validate_permissions

class ChannelPermissions(commands.Cog):
    """
    Commands for managing the channel permissions of the LLM.

    Allow or disallow the LLM from speaking in a certain channel.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="allow_channel", description="Allow the AI to interact in this channel.")
    async def allow_channel(self, interaction: discord.Interaction):
        """
        Sets the channel to be allowed for the bot to interact in.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's action.
        """
        discord_obj.guild = interaction.guild
        discord_obj.bot_member = await discord_obj.guild.fetch_member(self.bot.user.id)
        discord_obj.bot_name = discord_obj.bot_member.display_name

        if not await validate_permissions(interaction):
                 return


        await config.allow_channel(interaction.channel)
        await interaction.response.send_message(
            f"{discord_obj.bot_name} will now interact in this channel.",
            ephemeral=False
        )

    @app_commands.command(name="disallow_channel", description=f"Disallow the AI to interact in this channel.")
    async def disallow_channel(self, interaction: discord.Interaction):
        """
        Sets the channel to be disallowed for the bot to interact in.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's action.
        """
        discord_obj.guild = interaction.guild
        discord_obj.bot_member = await discord_obj.guild.fetch_member(self.bot.user.id)
        discord_obj.bot_name = discord_obj.bot_member.display_name

        if not await validate_permissions(interaction):
                 return


        if await config.disallow_channel(interaction.channel):
            await interaction.response.send_message(
            f"{discord_obj.bot_name} will no longer interact in this channel.",
            ephemeral=False
        )
        else:
                await interaction.response.send_message(
                f"{discord_obj.bot_name} is already not allowed to interact in this channel.",
                ephemeral=False
            )
                
async def setup(bot: commands.Bot):
    await bot.add_cog(ChannelPermissions(bot))
     
