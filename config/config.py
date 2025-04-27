import json
import discord
import asyncio
from bot.discord_obj_processor import discord_obj

class Config:
    def __init__(self):
        self.guild_models = {}
        self.guild_sys_prompts = {}
        self.guild_allowed_channels_id = {}
        self.model_list = {}
        self.help_commands = {}
        self._save_lock = asyncio.Lock()

        self.load_config()

        self.default_sys_prompt = f"You are an AI assistant in a Discord chat with multiple users."
        self.default_model = "gemini-2.0-flash-lite"

    def load_config(self):
        # List the attribute names that need configuration.
        for attr in ["guild_models", "guild_sys_prompts", "guild_allowed_channels_id", "model_list", "help_commands"]:
            with open(f"config/config.json", "r") as file:
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
        async with self._save_lock: 
            with open(f"config/config.json", "r") as file:
                config_file = json.load(file)
                config_file[f"{attr}"] = data
            with open(f"config/config.json", "w") as file:
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

    async def save_selected_model(self, model: str):
        """
        Saves the model of the bot given the guild object and refreshes the message manager
        with the same model.

        Args:
            model (str): The string corresponding to the new selection.
            guild (discord.Guild): Guild object. 
        """
        await self.create_model_default()

        key = str(discord_obj.guild.id)
        self.guild_models[key] = model  
        await self.save_config("guild_models", self.guild_models)

    async def current_model(self) -> str:
        """
        Gets the current model of the given guild.
        """
        await self.create_model_default()
        return self.guild_models[str(discord_obj.guild.id)]
    
    # Methods for system messages.
    
    async def modify_sys_prompt(self, sys_prompt: str) -> None:
        """
        Modifies the system prompt given the system prompt and the guild.

        Args:
            sys_prompt (str): The new system prompt to replace the old one with.
        """
        key = str(discord_obj.guild.id)

        self.guild_sys_prompts[key] = sys_prompt
        await self.save_config("guild_sys_prompts", self.guild_sys_prompts)
        return await self.initialize_system_prompt()


    async def initialize_system_prompt(self) -> None:
        """
        Creates a system prompt given the guild object if it doesn't already exist and updates it if it already exists.
        """
        key = str(discord_obj.guild.id)
        # Check if the key is in the system prompts dictionary
        if not key in self.guild_sys_prompts:
            self.guild_sys_prompts[key] = self.default_sys_prompt # If it isn't, then create a new one with the default message.
            await self.save_config("guild_sys_prompts", self.guild_sys_prompts) 

        # Check if the name is in the system prompt
        if not "$name" in self.guild_sys_prompts[key]:
            self.guild_sys_prompts[key] =  f"{self.guild_sys_prompts[key]} Your name is $name"
            await self.save_config("guild_sys_prompts", self.guild_sys_prompts)

        formatted_sys_prompt: str = self.guild_sys_prompts[key].replace("$name", discord_obj.bot_name)
        return formatted_sys_prompt

    # Channel permission methods.

    async def allow_channel(self, channel: discord.TextChannel=None) -> None:
        """
        Adds a channel to the list of allowed channels.
        """
        
        key = str(channel.guild.id)
     
        if key in self.guild_allowed_channels_id:
            if channel.id not in self.guild_allowed_channels_id[key]:
                self.guild_allowed_channels_id[key].append(channel.id)
                await self.save_config("guild_allowed_channels_id", self.guild_allowed_channels_id)
        else:
            self.guild_allowed_channels_id[key] = [channel.id]
            await self.save_config("guild_allowed_channels_id", self.guild_allowed_channels_id)

    async def disallow_channel(self, channel: discord.TextChannel=None) -> bool:
        """
        Removes a channel to the list of allowed channels.

        Returns:
            bool: Returns True if the operation was successful and False it it wasn't.
        """
    
        key = str(channel.guild.id)

        try: # Try to remove the channel from the list of allowed channels.
            self.guild_allowed_channels_id[key].remove(channel.id) # Will except if no channels with that ID exist.
            if len(self.guild_allowed_channels_id[key]) - 1 < 0: # If the length of the list inside the dictionary is less than 0...
                del self.guild_allowed_channels_id[key] #... remove the dictionary entirely. This means that if the dictionary has no items in its list it will be removed.
            await self.save_config("guild_allowed_channels_id", self.guild_allowed_channels_id)
            return True
        except (ValueError, KeyError):
            return False
        
    async def delete_guild_vars(self, guild: discord.Guild) -> None:
        """
        Delete the guild's every stored variable from the config.
        """
        key = str(guild.id)
        del self.guild_allowed_channels_id[key]
        del self.guild_models[key]
        del self.guild_sys_prompts[key]
        await self.save_config("guild_allowed_channels_id", self.guild_allowed_channels_id)
        await self.save_config("guild_models", self.guild_models)
        await self.save_config("guild_sys_prompts", self.guild_sys_prompts)

    async def set_guild_vars_default(self, guild: discord.Guild) -> None:
            """
            Set the guild's every stored variable from the config to defaults.
            """
            key = str(guild.id)
            self.guild_models[key] = self.default_model
            self.guild_sys_prompts[key] = self.default_sys_prompt

            await self.save_config("guild_models", self.guild_models)
            await self.save_config("guild_sys_prompts", self.guild_sys_prompts)

    def get_conversation_thread_id(self, interaction: discord.Interaction) -> str:
         if interaction.guild:
             # For guild channels, use guild ID + channel ID string
             # Use interaction.guild_id and interaction.channel_id which are directly available
             return f"{interaction.guild_id}-{interaction.channel_id}"
         else:
             # For DMs, just use the channel ID string
             return str(interaction.channel_id)


config = Config()