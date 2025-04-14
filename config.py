import json
import discord
from discord_obj_processor import discord_obj_processor

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

    async def create_model_default(self):
        """
        Creates the default model for the bot given the guild object if it hasn't been set yet,
        and updates the message manager with the corresponding guild's set model.
        """
        key = str(discord_obj_processor.guild.id)
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
        return self.guild_models[str(discord_obj_processor.guild.id)]
    
    
    

    

            


config = Config()
    
