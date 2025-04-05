from tauleph_discord_bot import bot
from utils.extract_thinking import extract_think
from utils.split_into_chunks import split_text_into_chunks


import discord


import logging


class UIMessageHandler:
    """
    Handles all the UI (Discord).

    Manages regeneration buttons, Discord message types (discord.Interaction and discord.Message), and
    sending messages.
    """
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        filename='tauleph_messages.log')
    logger = logging.getLogger('tauleph_messages')
    def __init__(self):
        # Newest_messages holds the newest messages that the bot has sent.
        self.newest_messages = []
        self.regen_buttons = "" # The RegenButtons class is instantiated in this variable.
        self.is_interaction = False

    async def send_llm_output(self, llm_output: str, discord_object):
        """
        Sends the LLM output to the channel the message was sent in.

        Handles both regenerations (discord.Interaction) and normal messages (discord.Message). 

        Args:
            llm_output (str): The LLM output to send.
            discord_object (discord.Message/Interaction): The Discord object to take as reference.
        """
        self.is_interaction=await self._determine_interaction_or_message(discord_object)
        await self._prepare_response(llm_output, discord_object)

    async def _determine_interaction_or_message(self, discord_object):
        """
        Determines if the message corresponds to an interaction (regenediscord.InteractionType.componentrations) or a message.

        Args:
            discord_object (discord.Message/Interaction): The Discord object to process.
        Returns: 
            bool: Returns False if the Discord object is a message. Returns True if it is an interaction.
        Raises:
            TypeError: The given Discord object is incorrect or it isn't supported yet.
        """

        if discord_object in (discord.MessageType.default, discord.MessageType.reply):
            return False
        elif discord_object in (discord.InteractionType.component,):
            return True
        else:
            raise ValueError(f"Unsupported message type: {discord_object}")

    async def _prepare_response(self, llm_output, discord_object):
        """
        Prepare the response for Discord.

        Logs the conversation, prepares the new responses and finally sends the chunked responses
        if the message is longer than 2000 characters.

        Args:
            llm_output (str): The LLM output to send.
            discord_object (discord.Message/Interaction): The Discord object to take as reference.
        """
        await self._log_conversation(llm_output, discord_object)
        await self._prepare_new_responses()
        await self._chunk_responses(llm_output, discord_object)

    async def _chunk_responses(self, llm_output, discord_object):
        """
        Chunks the responses and then sends them into Discord and adds the RegenButtons view if the 
        chunk is the last chunk.

        Args:
            llm_output (str): The LLM output to send.
            discord_object (discord.Message/Interaction): The Discord object to take as reference.
        """

        output_chunks = await self._chunked_output(llm_output)

        for i, chunk in enumerate(output_chunks):
            is_last_chunk = i == (len(output_chunks)-1)
            view = self.regen_buttons if is_last_chunk else None
            newest_llm_message = await self._send_message(discord_object, chunk, view, output_chunks)
            self.newest_messages.append(newest_llm_message)

    async def _send_message(self, discord_object, chunk, view, output_chunks):
        """
        Sends the messages to Discord.

        It either uses discord.Interaction.followup or discord.Interaction.edit if it's an interaction,
        and simply uses discord.Message.reply if it's a normal message.

        Args:
            discord_object (discord.Message/Interaction): The Discord object to take as reference.
            chunk (str): The chunk to be sent.
            view (discord.ui.Button): The view to apply to the message.
            output_chunks (list): The entire chunk list, including all the chunks.
        """
        if self.is_interaction:
            if len(output_chunks)>1:
                return await discord_object.followup.send(content=chunk, view=view)
            else:
                return await self.newest_messages[-1].edit(content=chunk, view=view)
        else:
            return await discord_object.reply(chunk, mention_author=True, view=view)

    async def _chunked_output(self, text):
        """
        Chunks the output of the LLM and removes the thinking tags if there are any.

        Args:
            text (str): The text to be formatted.
        Returns:
            list: A list containing every chunk.
        """
        processing1_llm_output = extract_think(text)[0]

        if len(processing1_llm_output) > 2000:
            return split_text_into_chunks(processing1_llm_output, 2000)
        else:
            return [processing1_llm_output]

    async def _log_conversation(self, llm_output, discord_object):
        """
        Logs the conversation in the console.

        Args:
            llm_output (str): The output to print in console.
            discord_object (discord.Message/Interaction): The Discord object to take as reference.
        """
        names_list=await bot.get_names_list(discord_object, self.is_interaction)
        bot_name=names_list[0]
        username=names_list[1]
        user_msg=names_list[2]
        if self.is_interaction:
            self.logger.info(f"{bot_name}: {llm_output}")
        else:
            self.logger.info(f"{username}: {user_msg}")
            self.logger.info(f"{bot_name}: {llm_output}")


    async def _prepare_new_responses(self):
        """
        Prepares the UI state for new messages by clearing previous states.

        This includes clearing the newest messages, previous views, and deleting old messages if necessary.
        """

        await self._clear_newest_messages()
        if not self.is_interaction:
            await self._clear_previous_view()
            await self._delete_previous_messages()

    async def _delete_previous_messages(self):
        """
        Deletes all but the last message in the newest messages list if there are multiple messages.
        """
        for message in self.newest_messages: # Delete the newest messages if there are any.
                if len(self.newest_messages) > 1:
                    await message.delete()
                    self.newest_messages=[] # Clear the message list for new ones.
                else:
                    break

    async def _clear_newest_messages(self):
        """
        Updates the newest messages list to only include the last message if there are multiple messages.
        """
        if len(self.newest_messages) > 1:
            self.newest_messages=[self.newest_messages[-1]]

    async def _clear_previous_view(self):
        """
        Removes the view (buttons) from the last message in the newest messages list.
        """
        if self.newest_messages:
            await self.newest_messages[-1].edit(view=None)