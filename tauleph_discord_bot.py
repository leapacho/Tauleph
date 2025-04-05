import discord
from discord.ext import commands
from discord import app_commands
from colorama import init
import os
from main import llm_config, message_manager, ui_msg_handler, _entry_point
from dotenv import load_dotenv
from typing import Literal


# Initiate colorama.
init()

# Load the environment variables.
load_dotenv()

# Initialize the class of the message manager and the intents.
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MyBot(commands.Bot):
    """
    Main Discord bot class.
    """
    def __init__(self, command_prefix, *, help_command = ...,  intents, **options):
        super().__init__(command_prefix, help_command=help_command, intents=intents, **options)
        
    async def get_guild_name(self, guild: discord.Guild) -> str:
        """
        Returns the guild name given the guild object. 

        It retrieves the global_name or the name if global_name isn't available.

        Args:
            guild (discord.Guild): The guild's object.
        """
        bot_member = await guild.fetch_member(self.user.id)
        bot_name = bot_member.display_name
        return bot_name

    async def get_names_list(self, discord_object, is_interaction: bool=False):
        """
        Gets a list of names that contains the bot's name, the user's name, and the user's message.

        Args:
            discord_object (discord.Message/Interaction): The Discord object to take as reference.
            is_interaction (bool): 
        """
        user_msg = ""
        
        # Fetches the user object
        try:
            fetch=await bot.fetch_user(discord_object.user.id) if is_interaction else await bot.fetch_user(discord_object.author.id) 
            user_msg = discord_object.content if not is_interaction else None
        except AttributeError as err:
            raise ValueError("Erroneous Discord object. Try setting is_interaction to False.") from err
        
        username = fetch.display_name
       
        guild = discord_object.guild
        bot_name=await self.get_guild_name(guild=guild)

        names_list = [bot_name, username, user_msg]

        return names_list
    
    async def init_variables(self, guild: discord.Guild):
        """
        Initiates necessary variables.
        """
        await llm_config.create_sys_prompt_default(guild=guild)
        await llm_config .create_model_default(guild=guild)
        message_manager.refresh_model(llm_config.models[str(guild.id)])
        message_manager.update_thread_id(thread_id=guild.id)

    async def history_messages(self):
        """
        Saves the last 15 messages in the channel the message was sent in into a pickle file.

        This is for an LLM tool that loads the 15 most recent messages into its memory, not the bot's memory itself.

        Args:
            channel (discord.Message.channel): The channel to retrieve messages from.
        """

        channel = ui_msg_handler.newest_messages[-1].channel
        message_list=[]
        async for history_message in channel.history(limit=15,oldest_first=False):
            h_msg=history_message.content
            h_user=history_message.author.global_name or history_message.author.name
            h_msg_user=f"{h_user}: {h_msg}"
            message_list.append(h_msg_user)
            return message_list
  
    async def is_eligible_message(self, message: discord.Message) -> bool:
        """
        Checks whether the message is a bot call or a message from itself, and 
        if it comes from an allowed channel.

        Args:
            message (discord.Message): The message to take as reference.
        Returns:
            bool: Whether it was a bot call or not.
        """
        if message.author.id == self.user.id:
            return False
        
        bot_name = await self.get_guild_name(message.guild)

        is_allowed_channel = message.channel.id in llm_config.allowed_channels[str(message.guild.id)]

        bot_name_in_message = is_allowed_channel and bot_name.lower() in message.content.lower() # True if the bot's name is in the message and it comes from an allowed channel.
        bot_mentioned = is_allowed_channel and self.user in message.mentions # True if the bot is mentioned in the message and it comes from an allowed channel.

        return bot_name_in_message or bot_mentioned

    async def on_guild_join(self, guild: discord.Guild):
        """
        Sends a message to the guild when the bot joins it.

        See Discord.py's API reference for more details on this method.
        """
        guild_channels=guild.text_channels
        for channel in guild_channels:
            try:
                await channel.send("This is Tauleph, a simple AI chatbot. To get started, use the command `/help quickstart` or `/help commands`")
                return
            except discord.Forbidden: # discord.Forbidden is an exception. It's raised when the bot tries to send a message to a channel
                continue              # it isn't allowed to send messages in.
        

    async def on_ready(self):
        """
        Synchronizes the command tree and the bot's status.

        See Discord.py's API reference for more details on this method.
        """
        global bot
        await bot.tree.sync()
        print(f"hai ai am bot readi uwu. ai am loged in as {self.user}. miii id is {self.user.id}")
        print("----------------------------------------------------------------------------------")

    async def on_message(self, message: discord.Message):
        """
        Main function that handles the bot's responses to messages.

        See Discord.py's API reference for more details on this method.
        """
        if not await self.is_eligible_message(message):
            return
        
        await self._prepare_message_context(message)
        await self._process_and_respond(message)
        

    async def _prepare_message_context(self, message: discord.Message):
        """
        Prepares the context for processing a message.

        Initializes necessary variables and sets up the regeneration buttons.

        Args:
            message (discord.Message): The message to take as reference.
        """ 
        guild: discord.Guild = message.guild 
        await self.init_variables(guild) 
        # await self.history_messages(message.channel) # Save the last 15 messages in the channel.
        ui_msg_handler.regen_buttons = RegenButtons() # Instantiates the class here to let the event loop start running.

    async def _process_and_respond(self, message: discord.Message):
        """
        Processes the given message and sends the appropriate response.

        Args:
            message (discord.Message): The message to process.
        """
        # Start the message processing flow.
        await _entry_point(message)



bot = MyBot(command_prefix="", intents=intents, help_command=None)



class ModelSelect(discord.ui.Select):
    """
    Creates a custom Select (dropdown) class for selecting LLM models.
    """

    def __init__(self, llm_provider):
        """
        Initializes the dropdown with options for Groq and Google models.

        Args:
            llm_provider (str): The LLM provider to display a dropdown for.
        """
        self.llm_provider = llm_provider
        options = []
        if "groq" in llm_provider:
            comment = "6K max tokens."
            
        if "google" in llm_provider:
            comment = "Some are heavily rate limited."

        for model in llm_config.model_list[llm_provider]:
            option = discord.SelectOption(
                label=model,
                value=model,
                description=comment
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
        await llm_config.save_selected_model(selected_model, guild)
        await interaction.message.delete()


class ModelSelectView(discord.ui.View):
    """
    Creates a View that holds the dropdown for selecting LLM models.
    """

    def __init__(self, llm_provider):
        """
        Initializes the view with the dropdown.

        Args:
            groq (bool): Whether to include Groq models in the dropdown.
            google (bool): Whether to include Google models in the dropdown.
        """
        super().__init__()
        self.add_item(ModelSelect(llm_provider))


@bot.tree.command(name="select_model", description="Select an LLM model.")
async def select_model(interaction: discord.Interaction, llm_provider: Literal["groq", "google"]):
    """
    Changes and updates the guild's selected model. 
    """
    # have a thingy that updates the dropdown menu options!!
    # Sets the view of the dropdown menu.
    view = ModelSelectView(llm_provider)

    await interaction.response.send_message(
        "Please select an LLM model from the dropdown below:",
        view=view,
        ephemeral=False  
    )


@bot.tree.command(name="current_model", description="The current selected LLM model.")
async def current_model(interaction: discord.Interaction):
    """
    Sends a message with the guild's selected model.
    """
    guild: discord.Guild = interaction.user.guild
    llm_model = await llm_config.current_model(guild)

    await interaction.response.send_message(
        f"The current LLM model is: **{llm_model}**",
        ephemeral=False
    )

@bot.tree.command(name="change_system_message", description=f"Change the system message of the LLM.")
async def change_system_message(interaction: discord.Interaction, sys_message: str):
    """
    Sets the system message of the bot in the guild given the system message.

    Args:
        interaction (discord.Interaction): The interaction object representing the user's action.
        sys_message (str): The new system message to set.
    """
    guild: discord.Guild = interaction.user.guild
    if len(sys_message) < 2000:
        sys_prompts=await llm_config.modify_sys_prompt(guild, sys_message)

        await interaction.response.send_message(
            f"System message has been changed to '{sys_prompts[str(guild.id)]}'",
            ephemeral=False
        )
    else:
        await interaction.response.send_message(
            f"System message cannot be longer than 2000 characters.",
            ephemeral=False
        )

@bot.tree.command(name="current_system_message", description=f"Check the current system message of the LLM.")
async def current_system_message(interaction: discord.Interaction):
    """
    Sends a message with the guild's current system message.

    Args:
        interaction (discord.Interaction): The interaction object representing the user's action.
    """
    guild: discord.Guild = interaction.user.guild
    sys_prompts = await llm_config.create_sys_prompt_default(guild=guild)


    await interaction.response.send_message(
        f"The current system message is '{sys_prompts[str(guild.id)]}'",
        ephemeral=False
    )

@bot.tree.command(name="channel_allow", description=f"Allow the AI to interact in this channel.")
async def channel_allow(interaction: discord.Interaction):
    """
    Sets the channel to be allowed for the bot to interact in.

    Args:
        interaction (discord.Interaction): The interaction object representing the user's action.
    """
    guild: discord.Guild = interaction.user.guild
    bot_name=await bot.get_guild_name(guild=guild)

    channel=interaction.channel_id
    await llm_config.allow_channel(channel, guild)
    await interaction.response.send_message(
        f"{bot_name} will now interact in this channel.",
        ephemeral=False
    )

@bot.tree.command(name="channel_disallow", description=f"Disallow the AI to interact in this channel.")
async def channel_disallow(interaction: discord.Interaction):
    """
    Sets the channel to be disallowed for the bot to interact in.

    Args:
        interaction (discord.Interaction): The interaction object representing the user's action.
    """
    guild: discord.Guild = interaction.user.guild # Get the guild
    bot_name=await bot.get_guild_name(guild=guild) # Get the guild's nickname

    channel=interaction.channel_id
    if await llm_config.disallow_channel(channel, guild):
        await interaction.response.send_message(
        f"{bot_name} will no longer interact in this channel.",
        ephemeral=False
    )
    else:
            await interaction.response.send_message(
            f"{bot_name} is already not allowed to interact in this channel.",
            ephemeral=False
        )



# View class for regeneration buttons.
class RegenButtons(discord.ui.View):
    """
    View class for regeneration buttons.
    """
    def __init__(self):
        super().__init__()

    async def _on_navigation_change(self):
        """
        Updates the navigation buttons' state and labels based on the current navigation indices.

        Enables or disables buttons and updates the repeat button label with the current indices.
        """
        self.children[0].disabled=message_manager.can_go_backward  # self.children is a class attribute that holds the views  
        self.children[1].disabled=message_manager.can_go_forward   # that have been created in the class.
        self.children[2].label=f"🔁 {message_manager.indices}"  # Update the repeat button with new indices.

    # Button views.
    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.blurple, disabled=True)
    async def left_navigation_button(self, interaction: discord.Interaction, button: discord.Button):
        
        await interaction.response.defer() # Defer the response to avoid having the
                                           # "Interaction failed" warning on the Discord message.
        regen_msg = message_manager.navigate_backward() 
        await self._on_navigation_change()

        await ui_msg_handler.send_llm_output(regen_msg, interaction)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.blurple, disabled=True)
    async def right_navigation_button(self, interaction: discord.Interaction, button: discord.Button):

        await interaction.response.defer()

        regen_msg = message_manager.navigate_forward()
        await self._on_navigation_change()

        await ui_msg_handler.send_llm_output(regen_msg, interaction)

    @discord.ui.button(label="🔁", style=discord.ButtonStyle.blurple)
    async def regeneration_button(self, interaction: discord.Interaction, button: discord.Button):

        await interaction.response.defer()

        regen_msg = message_manager.regenerate()
        await self._on_navigation_change()

        await ui_msg_handler.send_llm_output(regen_msg, interaction)

group = app_commands.Group(name="help", description="Help command. Shows useful information about Tauleph.")

# These next few lines are merely help commands that send a message to the user with information about the bot.
@group.command(name="quickstart", description="A quick guide on how to start using Tauleph.")
async def quickstart(interaction: discord.Interaction):
    """
    Sends a quickstart guide message to the user.

    Args:
        interaction (discord.Interaction): The interaction object representing the user's action.
    """
    await interaction.response.send_message(llm_config.help_commands["quickstart"])

@group.command(name="commands", description="See what each commands does.")
async def bot_commands(interaction: discord.Interaction):
    """
    Sends a message listing all available commands to the user.

    Args:
        interaction (discord.Interaction): The interaction object representing the user's action.
    """
    await interaction.response.send_message(llm_config.help_commands["commands"])

@group.command(name="functionality", description="See what functionality Tauleph has.")
async def functionality(interaction: discord.Interaction):
    """
    Sends a message describing the bot's functionality to the user.

    Args:
        interaction (discord.Interaction): The interaction object representing the user's action.
    """
    await interaction.response.send_message(llm_config.help_commands["functionality"])


bot.tree.add_command(group) # Adds these commands as a group to the command tree.

bot.run(os.environ.get("BOT_API_KEY"))