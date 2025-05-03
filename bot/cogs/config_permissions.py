import discord
from discord.ext import commands
from discord import app_commands
from config.config import config
from utils.validation import validate_permissions

class ConfigPermissions(commands.Cog):
    def __init__(self):
        pass
    
    @app_commands.command(name="set_role", description="Set the role users need to edit Tauleph's settings. Admin only command.")
    async def set_role(self, interaction: discord.Interaction, role: str):
            if not await validate_permissions(interaction, admin_only=True):
                 return
            if role.startswith("<@&") and role.endswith(">") and len(role) == 23:
                await config.save_role(role, interaction.guild)
                await interaction.response.send_message(content=f"Succesfully set the role to {role}")
            else:
                 await interaction.response.send_message(content=f"{role} is not a valid role.")

async def setup(bot: commands.Bot):
    await bot.add_cog(ConfigPermissions())
     