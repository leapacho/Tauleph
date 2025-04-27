import discord
from discord.ext import commands
from discord import app_commands

from config.config import config
from bot.discord_obj_processor import discord_obj
from llm_graph.graph import graph
from llm_graph.checkpoint_manager import checkpoint_manager

class SetGuildDefault(commands.Cog):
    """
    Command for setting all the settings of the LLM to their defaults.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="set_settings_to_default", description="Set every setting to their default.")
    async def set_settings_to_default(self, interaction: discord.Interaction):
        """
        Sets every guild variable to their default.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's action.
        """
        discord_obj.guild = interaction.guild
        discord_obj.bot_member = await discord_obj.guild.fetch_member(self.bot.user.id)
        discord_obj.bot_name = discord_obj.bot_member.display_name


        await config.set_guild_vars_default(interaction.guild)
        await interaction.response.send_message(
            f"{discord_obj.bot_name}'s settings are now default.",
            ephemeral=False
        )
    
    @app_commands.command(name="clear_memory", description="Clear the bot's memory permanently.")
    async def clear_memory(self, interaction: discord.Interaction):
        """
        Clears the bot's memory permanently.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's action.
        """
        discord_obj.guild = interaction.guild
        discord_obj.bot_member = await discord_obj.guild.fetch_member(self.bot.user.id)
        discord_obj.bot_name = discord_obj.bot_member.display_name

        thread_id = f"{discord_obj.guild.id}"
        print(thread_id)

        await graph.clear_history(thread_id)
        checkpoint_manager.ai_configs = []
        await interaction.response.send_message(
            f"{discord_obj.bot_name}'s memory has been cleared.",
            ephemeral=False
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(SetGuildDefault(bot))
     
