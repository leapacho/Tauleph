from tauleph_discord_bot import bot, message_manager

import discord

import json
from json.decoder import JSONDecodeError

class LLMConfigManager:
    """
    Manages several LLM configurations.

    Manages the system prompts, models, and allowed channels with a per-guild basis, as well as
    loading the help command texts.
    All of the configurations are saved in their respective json files, named identically
    to their variable names. 
    """
    def __init__(self):
        self.models = {}
        self.sys_prompts = {}
        self.allowed_channels = {}
        self.model_list = {}
        self.help_commands = {}

        self.load_config()

    def load_config(self):
        # List the attribute names that need configuration.
        for attr in ["models", "sys_prompts", "allowed_channels", "model_list", "help_commands"]:
            try:
                with open(f"json_configs/{attr}.json", "r") as file:
                    data=json.load(file)
            except (FileNotFoundError, JSONDecodeError):
                data={1:2} # Sets it to an arbitrary value so we can always create the file even if there's no allowed channels.
                with open(f"json_configs{attr}.json", "w") as file:
                    json.dump(data, file)
                # Update the attribute on the instance.
            setattr(self, attr, data)

    async def save_config(self, attr, data):
        """
        Saves the given configuration data to a JSON file.

        Args:
            attr (str): The name of the attribute to save.
            data (dict): The data to save in the JSON file.
        """
        with open(f"json_configs/{attr}.json", "w") as file:
            json.dump(data, file)

    async def current_model(self, guild: discord.Guild) -> str:
        """
        Gets the current model of the given guild.
        """
        await self.create_model_default(guild)
        return self.models[str(guild.id)]

    async def create_model_default(self, guild: discord.Guild):
        """
        Creates the default model for the bot given the guild object if it hasn't been set yet,
        and updates the message manager with the corresponding guild's set model.
        """
        key = str(guild.id)
        if not key in self.models.keys():
            self.models[key] = "gemini-2.0-flash-lite"
            await self.save_config("models", self.models)
        message_manager.refresh_model(self.models[key])

    async def save_selected_model(self, model: str, guild: discord.Guild):
        """
        Saves the model of the bot given the guild object and refreshes the message manager
        with the same model.

        Args:
            model (str): The string corresponding to the new selection.
            guild (discord.Guild): Guild object. 
        """
        await self.create_model_default(guild)

        key = str(guild.id)
        self.models[key] = model
        message_manager.refresh_model(self.models[key])
        await self.save_config("models", self.models)


    async def allow_channel(self, channel_id: int, guild: discord.Guild):
        """
        Adds a channel to the list of allowed channels.

        Args:
            channel_id (int): The ID of the channel to allow.
            guild (discord.Guild): The guild object.
        """
        key = str(guild.id)
        if key in self.allowed_channels.keys():
            self.allowed_channels[key].append(channel_id)
            await self.save_config("allowed_channels", self.allowed_channels)
        else:
            self.allowed_channels[key] = [channel_id]
            await self.save_config("allowed_channels", self.allowed_channels)

    async def disallow_channel(self, channel_id: int, guild: discord.Guild) -> bool:
        """
        Removes a channel to the list of allowed channels.

        Args:
            channel_id (int): The ID of the channel to disallow.
            guild (discord.Guild): The guild object.
        Returns:
            bool: Returns True if the operation was successful and False it it wasn't.
        """
        key = str(guild.id)
        try: # Try to remove the channel from the list of allowed channels.
            self.allowed_channels[key].remove(channel_id) # Will except if no channels with that ID exist.
            await self.save_config("allowed_channels", self.allowed_channels)
            return True
        except ValueError:
            return False

    async def modify_sys_prompt(self, guild: discord.Guild, sys_prompt: str) -> dict:
        """
        Modifies the system prompt given the system prompt and the guild.

        Args:
            sys_prompt (str): The new system prompt to replace the old one with.
            guild (discord.Guild): Guild object.
        Returns:
            str: The new system prompt.
        """
        key = str(guild.id)

        self.sys_prompts[key] = sys_prompt
        await self.save_config("sys_prompts", self.sys_prompts)
        await self.create_sys_prompt_default(guild)
        return self.sys_prompts

    async def create_sys_prompt_default(self, guild: discord.Guild) -> str:
        """
        Creates a system prompt given the guild object if it doesn't already exist.

        Args:
            guild (discord.Guild): Guild object.
        Returns:
            str: The default system prompt. # fix sys prompt 2000 char+ exploit
        """
        key = str(guild.id)
        bot_name=await bot.get_guild_name(guild)

        # Check if the key is in the system prompts dictionary
        if not key in self.sys_prompts.keys():
            self.sys_prompts[key] = f"You are an AI assistant called {bot_name} in a Discord chat with multiple users." # If it isn't, then create a new one with the default message.
            await self.save_config("sys_prompts", self.sys_prompts)
        # Check if the name is in the system prompt
        if not bot_name in self.sys_prompts[key]:
            self.sys_prompts[key] += f" Your name is {bot_name}." # If it isn't, then add the bot's name into it
            await self.save_config("sys_prompts", self.sys_prompts)
        return self.sys_prompts