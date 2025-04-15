import discord
from discord.ext import commands
from discord import app_commands
from config import config
from discord_obj_processor import discord_obj


class ModelSelect(discord.ui.Select):
    """
    Creates a custom Select (dropdown) class for selecting LLM models.
    """

    def __init__(self):
        """
        Initializes the dropdown with options for Google models.
        """

        options = []
        for model in config.model_list:
            option = discord.SelectOption(
                label=model,
                value=model,
            )
            options.append(option)
            
        super().__init__(placeholder="Choose an LLM...", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        """
        Handles the user's selection from the dropdown menu.

        Sends a message with the selected model and updates the guild's configuration.

        Args:
            interaction (discord.Interaction): The interaction object representing the user's action.
        """
        selected_model = self.values[0]
        guild: discord.Guild = interaction.message.guild
        await interaction.response.send_message(
            f"Selected model: **{selected_model}**",
            ephemeral=False
        )
        await config.save_selected_model(selected_model, guild)
        await interaction.message.delete()


class ModelSelectView(discord.ui.View):
    """
    Creates a View that holds the dropdown for selecting LLM models.
    """

    def __init__(self):
        """
        Initializes the view with the dropdown.
        """
        super().__init__()
        self.add_item(ModelSelect())

class SelectModel(commands.Cog):
    """
    Command for letting users select their desired LLM model.
    """
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="select_model", description="Select an LLM model.")
    async def select_model(self, interaction: discord.Interaction):
        """
        Changes and updates the guild's selected model. 
        """

        # Sets the view of the dropdown menu.
        view = ModelSelectView()

        await interaction.response.send_message(
            "Please select an LLM model from the dropdown below:",
            view=view,
            ephemeral=False  
        )

    @app_commands.command(name="current_model", description="The current selected LLM model.")
    async def current_model(self, interaction: discord.Interaction):
        """
        Sends a message with the guild's selected model.
        """
        discord_obj.guild = interaction.guild
        llm_model = await config.current_model()

        await interaction.response.send_message(
            f"The current LLM model is: **{llm_model}**",
            ephemeral=False
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(SelectModel(bot))