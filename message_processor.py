from discord_obj_processor import discord_obj
from discord_ui_handler import discord_ui_handler, RegenButtons
from config import config
import requests


class MessageProcessor:
    """
    Manages the processing of messages. 

    Serves like the bridge between Discord and Groq's API.
    """
    def __init__(self):
        self.message_template = f"{discord_obj.message_author} sent a message. Respond to it in a conversational manner: {discord_obj.message_content}"
        self.sys_prompt = ""

    async def process_message(self) -> str:
        """
        Processes the given message. 

        Can process images, audio and text, and then sends the output.
        """

        self.sys_prompt = await config.initialize_system_prompt()

        processing_methods={ # This dictionary allows for easy implementation of other processing methods.
            "image": self._process_image,
            "audio": self._process_audio,
            "": self._process_text # If att_type is empty then this is the default.
        }


        result = await self._determine_message_type(processing_methods)
        return result

    async def _determine_message_type(self, processing_methods: dict) -> str:
        """
        Determines if the message is an image, audio, or text and processes it accordingly.

        Args:
            processing_methods (dict): A dictionary mapping attachment types to processing methods.
        Returns:
            str: The result of the corresponding processing method.
        """
        for prefix, method in processing_methods.items():
            if discord_obj.att_type.startswith(prefix):
                result = await method() # Calls the corresponding method.
                return result

    async def _process_image(self) -> str:
        """
        Processes the image.

        Returns:
            str: The output of the LLM's processing of the image.
        """

        async with discord_obj.message.channel.typing():
            image_output=([
                {"type": "text", "text": self.message_template},
                {"type": "image_url", "image_url": discord_obj.att_url}
                ], 
                self.sys_prompt)
        return image_output

    async def _process_audio(self) -> str:
        """
        Processes the audio.

        Returns:
            str: The output of the LLM's processing of the image.
        """
        file = requests.get(discord_obj.att_url)

        async with discord_obj.message.channel.typing():
            speech_output=([{"type": "text", "text": self.message_template},
                            {"type": "media", "mime_type": discord_obj.att_type, "data": file.content}],
                            self.sys_prompt)
        return speech_output

    async def _process_text(self) -> str:
        """
        Processes the text given.

        Returns:
            str: The output of the LLM's processing of the text.
        """
        async with discord_obj.message.channel.typing():
                llm_output=([{
                    "type": "text",
                    "text": self.message_template
                }], 
                self.sys_prompt) # These lines made me rewrite the entirety of Tauleph one time.
        return llm_output