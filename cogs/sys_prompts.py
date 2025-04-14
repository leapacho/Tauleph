import discord
from discord.ext import commands
from discord import app_commands
from discord_obj_processor import discord_obj
from typing import Optional

from config import config

class SysPrompts(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="change_system_message", description=f"Change the system message of the LLM.")
    async def change_system_message(self, interaction: discord.Interaction, sys_message: str):
        """
        Sets the system message of the bot in the guild given the system message.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's action.
            sys_message (str): The new system message to set.
        """
        discord_obj.guild = interaction.guild
        discord_obj.bot_member = await discord_obj.guild.fetch_member(self.bot.user.id)
        discord_obj.bot_name = discord_obj.bot_member.display_name


        if len(sys_message) < 2000:
            await config.modify_sys_prompt(sys_message)

            await interaction.response.send_message(
                f"System message has been changed to '{config.guild_sys_prompts[str(discord_obj.guild.id)]}'",
                ephemeral=False
            )
        else:
            await interaction.response.send_message(
                f"System message cannot be longer than 2000 characters.",
                ephemeral=False
            )

    @app_commands.command(name="current_system_message", description=f"Check the current system message of the LLM.")
    async def current_system_message(self, interaction: discord.Interaction):
        """
        Sends a message with the guild's current system message.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's action.
        """
        discord_obj.guild = interaction.guild
        discord_obj.bot_member = await discord_obj.guild.fetch_member(self.bot.user.id)
        discord_obj.bot_name = discord_obj.bot_member.display_name

        await config.create_sys_prompt_default()


        await interaction.response.send_message(
            f"The current system message is '{config.guild_sys_prompts[str(discord_obj.guild.id)]}'",
            ephemeral=False
        )

    
    @app_commands.command(name="restore_system_message", description=f"Restore the default system message of the LLM.")
    async def restore_system_message(self, interaction: discord.Interaction):
        """
        Sets the system message of the bot in the guild to the set default.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's action.
        """
        discord_obj.guild = interaction.guild
        discord_obj.bot_member = await discord_obj.guild.fetch_member(self.bot.user.id)
        discord_obj.bot_name = discord_obj.bot_member.display_name

        await config.modify_sys_prompt(f"You are an AI assistant called {discord_obj.bot_name} in a Discord chat with multiple users.")

        await interaction.response.send_message(
            f"The system message has been set to the default: '{config.guild_sys_prompts[str(discord_obj.guild.id)]}'",
            ephemeral=False
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(SysPrompts(bot))