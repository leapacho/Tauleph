import discord
from discord.ext import commands
from discord import app_commands

from config import config

class HelpCommandsGroup(app_commands.Group):
    
    @app_commands.command()
    async def quickstart(self, interaction: discord.Interaction):
        """
        Sends a quickstart guide message to the user.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's action.
        """
        await interaction.response.send_message(config.help_commands["quickstart"])

    @app_commands.command()
    async def commands(self, interaction: discord.Interaction):
        """
        Sends a command guide message to the user.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's action.
        """
        await interaction.response.send_message(config.help_commands["commands"])

    @app_commands.command()
    async def functionality(self, interaction: discord.Interaction):
        """
        Sends a functionality guide message to the user.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's action.
        """
        await interaction.response.send_message(config.help_commands["functionality"])

async def setup(bot: commands.Bot):
    bot.tree.add_command(HelpCommandsGroup(name="help", description="Help command. Shows useful information about Tauleph."))