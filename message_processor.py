from discord_obj_processor import discord_obj_processor
from google import genai
from google.genai import types
import requests


class MessageProcessor:
    """
    Manages the processing of messages. 

    Serves like the bridge between Discord and Groq's API.
    """
    def __init__(self):
        pass

    async def process_message(self):
        """
        Processes the given message. 

        Can process images, audio and text, and then sends the output.
        """

        processing_methods={ # This dictionary allows for easy implementation of other processing methods.
            "image": self._process_image,
            "audio": self._process_audio,
            "": self._process_text # If att_type is empty then this is the default.
        }


        result = await self._determine_message_type(processing_methods)
        return result
        #await ui_msg_handler.send_llm_output(result, self.message) # Separate concerns:
                                                                   # Make this method return its value and
                                                                   # orchestrate the UI handling elsewhere.


    async def _determine_message_type(self, processing_methods: dict) -> str:
        """
        Determines if the message is an image, audio, or text and processes it accordingly.

        Args:
            processing_methods (dict): A dictionary mapping attachment types to processing methods.
        Returns:
            str: The result of the corresponding processing method.
        """
        for prefix, method in processing_methods.items():
            if discord_obj_processor.att_type.startswith(prefix):
                result = await method() # Calls the corresponding method.
                return result

    async def _process_image(self):
        """
        Processes the image.

        Returns:
            str: The output of the LLM's processing of the image.
        """

        async with discord_obj_processor.message.channel.typing():
            image_output=([
                {"type": "text", "text": f"{discord_obj_processor.message_author} has sent a message: {discord_obj_processor.message_content}"},
                {"type": "image_url", "image_url": discord_obj_processor.att_url}
                ], 
                "You are a helpful AI called Tauleph.")
        return image_output

    async def _process_audio(self):
        """
        Processes the audio.

        Returns:
            str: The output of the LLM's processing of the image.
        """
        file = requests.get(discord_obj_processor.att_url)

        async with discord_obj_processor.message.channel.typing():
            speech_output=([{"type": "text", "text": f"{discord_obj_processor.message_author} has sent a message: {discord_obj_processor.message_content}"},
                            {"type": "media", "mime_type": discord_obj_processor.att_type, "data": file.content}],
                            "You are a helpful AI called Tauleph.")
        # Note: The audio processing is not implemented yet.
        return speech_output

    async def _process_text(self):
        """
        Processes the text given.

        Returns:
            str: The output of the LLM's processing of the text.
        """
        async with discord_obj_processor.message.channel.typing():
                llm_output=([{
                    "type": "text",
                    "text": f"{discord_obj_processor.message_author} sent a message: {discord_obj_processor.message_content}"
                }], 
                "You are a helpful AI called Tauleph.")
        return llm_output