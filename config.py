import json
import discord
from discord_obj_processor import discord_obj

class Config:
    def __init__(self):
        self.guild_models = {}
        self.guild_sys_prompts = {}
        self.guild_allowed_channels_id = {}
        self.model_list = {}
        self.help_commands = {}

        self.load_config()

    def load_config(self):
        # List the attribute names that need configuration.
        for attr in ["guild_models", "guild_sys_prompts", "guild_allowed_channels_id", "model_list", "help_commands"]:
            with open(f"config.json", "r") as file:
                data=json.load(file)
                loaded_data=data[attr]
            # Update the attribute on the instance. 
            setattr(self, attr, loaded_data)

    async def save_config(self, attr, data):
        """
        Saves the given configuration data to a JSON file.

        Args:
            attr (str): The name of the attribute to save.
            data (dict): The data to save in the JSON file.
        """
        with open(f"config.json", "r") as file:
            config_file = json.load(file)
            
            config_file[f"{attr}"] = data


        with open(f"config.json", "w") as file:
            json.dump(config_file, file, indent=4)

    # Methods for models.
        
    async def create_model_default(self):
        """
        Creates the default model for the bot given the guild object if it hasn't been set yet,
        and updates the message manager with the corresponding guild's set model.
        """
        key = str(discord_obj.guild.id)
        if not key in self.guild_models.keys():
            self.guild_models[key] = "gemini-2.0-flash-lite"
            await self.save_config("guild_models", self.guild_models)

    async def save_selected_model(self, model: str, guild: discord.Guild):
        """
        Saves the model of the bot given the guild object and refreshes the message manager
        with the same model.

        Args:
            model (str): The string corresponding to the new selection.
            guild (discord.Guild): Guild object. 
        """
        await self.create_model_default()

        key = str(guild.id)
        self.guild_models[key] = model  
        await self.save_config("guild_models", self.guild_models)

    async def current_model(self) -> str:
        """
        Gets the current model of the given guild.
        """
        await self.create_model_default()
        return self.guild_models[str(discord_obj.guild.id)]
    
    # Methods for system messages.
    
    async def modify_sys_prompt(self, sys_prompt: str) -> dict:
        """
        Modifies the system prompt given the system prompt and the guild.

        Args:
            sys_prompt (str): The new system prompt to replace the old one with.
            guild (discord.Guild): Guild object.
        Returns:
            str: The new system prompt.
        """
        key = str(discord_obj.guild.id)

        self.guild_sys_prompts[key] = sys_prompt
        await self.save_config("guild_sys_prompts", self.guild_sys_prompts)
        await self.create_sys_prompt_default()


    async def create_sys_prompt_default(self) -> str:
        """
        Creates a system prompt given the guild object if it doesn't already exist.

        Args:
            guild (discord.Guild): Guild object.
        Returns:
            str: The default system prompt. 
        """
        key = str(discord_obj.guild.id)

        # Check if the key is in the system prompts dictionary
        if not key in self.guild_sys_prompts:
            self.guild_sys_prompts[key] = f"You are an AI assistant called {discord_obj.bot_name} in a Discord chat with multiple users." # If it isn't, then create a new one with the default message.
            await self.save_config("guild_sys_prompts", self.guild_sys_prompts)
        # Check if the name is in the system prompt
        print(discord_obj.bot_name.lower())
        print(self.guild_sys_prompts[key].lower())
        if not discord_obj.bot_name.lower() in self.guild_sys_prompts[key].lower():
            self.guild_sys_prompts[key] += f" Your name is {discord_obj.bot_name}." # If it isn't, then add the bot's name into it
            await self.save_config("guild_sys_prompts", self.guild_sys_prompts)


config = Config()
    
