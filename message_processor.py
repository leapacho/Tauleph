from tauleph_discord_bot import bot, llm_config, message_manager

class MessageProcessor:
    """
    Manages the processing of messages. 

    Serves like the bridge between Discord and Groq's API.
    """
    def __init__(self, message):
        self.message = message

        self.names = [0,1,2] # Placeholder values.

        # Unpacks the values from the names list.
        self.username = self.names[1]
        self.user_msg = self.names[2]

        self.guild = self.message.guild
        self.att_type = ""

        for att in message.attachments: # Gets the attachments in the message.
            self.att_type = att.content_type
            self.att_url = att.url

    async def process_message(self):
        """
        Processes the given message. 

        Can process images, audio and text, and then sends the output.
        """
        self.names = await bot.get_names_list(self.message)
        self.username = self.names[1]
        self.user_msg = self.names[2]

        processing_methods={ # This dictionary allows for easy implementation of other processing methods.
            "image": self._process_image,
            "audio": self._process_audio,
            "": self._process_text # If att_type is empty then this is the default.
        }


        result = await self._determine_message_type(processing_methods)
        return result, self.message
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
            if self.att_type.startswith(prefix):
                result = await method() # Calls the corresponding method.
                return result

    async def _process_image(self):
        """
        Processes the image.

        Returns:
            str: The output of the LLM's processing of the image.
        """

        async with self.message.channel.typing():
            image_output=([
                {"type": "text", "text": f"{self.username} has sent a message: {self.message.content}"},
                {"type": "image_url", "image_url": self.att_url}
                ], 
                llm_config.sys_prompts[str(self.guild.id)])
        return image_output

    async def _process_audio(self):
        """
        Processes the audio.

        Returns:
            str: The output of the LLM's processing of the image.
        """

        async with self.message.channel.typing():
            speech_output=([{"type": "text", "text": f"{self.username} has sent a message: {self.message.content}"}],
                            {"type": "media", "mimeType": self.att_type, "uri": self.att_url},
                            llm_config.sys_prompts[str(self.guild.id)])
        # Note: The audio processing is not implemented yet.
        return speech_output

    async def _process_text(self):
        """
        Processes the text given.

        Returns:
            str: The output of the LLM's processing of the text.
        """
        async with self.message.channel.typing():
                llm_output=([{
                    "type": "text",
                    "text": f"{self.username} sent a message:{self.message.content}"
                }], 
                llm_config.sys_prompts[str(self.guild.id)])
        return llm_output