import discord
from discord.ext import commands
from discord import app_commands

from config.config import config
from utils.validation import validate_permissions
from utils.retrieve_member import retrieve_member

class SysPrompts(commands.Cog):
    """
    Commands for modifying the system prompts of the bot.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="change_system_message", description=f"Change the system message of the LLM.")
    async def change_system_message(self, interaction: discord.Interaction, sys_message: str):
        """
        Sets the system message of the bot in the guild given the system message.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's action.
            sys_message (str): Specify where to place the bot's name with "$name". e.g: "$name" will be turned into "Tauleph".
        """
        bot_member: discord.Member = await retrieve_member(interaction, self.bot.user.id)
        bot_name = bot_member.display_name
        
        if not await validate_permissions(interaction):
                 return


        if len(sys_message) < 2000:
            new_sys_prompt = await config.modify_sys_prompt(sys_message, bot_name)

            await interaction.response.send_message(
                f"System message has been changed to '{new_sys_prompt}'",
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
        bot_member: discord.Member = await retrieve_member(interaction, self.bot.user.id)
        bot_name = bot_member.display_name

        current_sys_prompt = await config.initialize_system_prompt(interaction.guild, bot_name)


        await interaction.response.send_message(
            f"The current system message is '{current_sys_prompt}'",
            ephemeral=False
        )

    
    @app_commands.command(name="restore_system_message", description=f"Restore the default system message of the LLM.")
    async def restore_system_message(self, interaction: discord.Interaction):
        """
        Sets the system message of the bot in the guild to the set default.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's action.
        """
        bot_member: discord.Member = await retrieve_member(interaction, self.bot.user.id)
        bot_name = bot_member.display_name

        if not await validate_permissions(interaction):
                 return

        default_sys_prompt = await config.modify_sys_prompt(config.default_sys_prompt, bot_name)

        await interaction.response.send_message(
            f"The system message has been set to the default: '{default_sys_prompt}'",
            ephemeral=False
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(SysPrompts(bot))