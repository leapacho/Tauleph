import discord
from discord_obj_processor import discord_obj
from checkpoint_manager import checkpoint_manager


class DiscordUIHandler():
    """
    UI handler for message pagination and regeneration.
    """
    def __init__(self):
        self.regen_buttons: RegenButtons = None
        self.newest_messages: list = []
        
    async def send_message_regen(self, message: str):
        await self._delete_previous_messages()
        if len(message) > 1:
            for i, chunk in enumerate(message):
                is_last_chunk = i == (len(message)-1)
                view = self.regen_buttons if is_last_chunk else None
                newest_llm_message = await discord_obj.text_channel.send(chunk, view=view)
                self.newest_messages.append(newest_llm_message)
        else:
            view = self.regen_buttons
            newest_llm_message = await self.newest_messages[-1].edit(content=message[-1], view=view)
            self.newest_messages.append(newest_llm_message)    

    async def send_message(self, message: str):

        for i, chunk in enumerate(message):
            is_last_chunk = i == (len(message)-1)
            view = self.regen_buttons if is_last_chunk else None
            newest_llm_message = await discord_obj.text_channel.send(chunk, view=view)
            self.newest_messages.append(newest_llm_message)
        
    async def _prepare_new_responses(self):
        """
        Prepares the UI state for new messages by clearing previous states.

        This includes clearing the newest messages, previous views, and deleting previous messages if necessary.
        """

        await self._clear_newest_messages()
        await self._clear_previous_view()
        await self._delete_previous_messages()

    async def _delete_previous_messages(self):
        """
        Deletes all but the last message in the newest messages list if there are multiple messages.
        """
        for message in self.newest_messages: # Delete the newest messages if there are any.
                if len(self.newest_messages) > 1:
                    await message.delete()
                else:
                    break
        self.newest_messages=[] # Clear the message list for new ones.

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

discord_ui_handler = DiscordUIHandler() #fix missing required positional argument bot

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
        self.children[0].disabled=checkpoint_manager.can_go_backward  # self.children is a class attribute that holds the views  
        self.children[1].disabled=checkpoint_manager.can_go_forward   # that have been created in the class.
        self.children[2].label=f"🔁 {checkpoint_manager.indices}"  # Update the repeat button with new indices.

    # Button views.
    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.blurple, disabled=True)
    async def left_navigation_button(self, interaction: discord.Interaction, button: discord.Button):
        
        await interaction.response.defer() # Defer the response to avoid having the
                                           # "Interaction failed" warning on the Discord message.
        regen_msg = await checkpoint_manager.page_backwards() 
        await self._on_navigation_change()

        await discord_ui_handler.send_message_regen(regen_msg)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.blurple, disabled=True)
    async def right_navigation_button(self, interaction: discord.Interaction, button: discord.Button):

        await interaction.response.defer()

        regen_msg =  await checkpoint_manager.page_forwards()
        await self._on_navigation_change()

        await discord_ui_handler.send_message_regen(regen_msg)

    @discord.ui.button(label="🔁", style=discord.ButtonStyle.blurple)
    async def regeneration_button(self, interaction: discord.Interaction, button: discord.Button):

        await interaction.response.defer()

        regen_msg = await checkpoint_manager.regeneration()
        await self._on_navigation_change()

        await discord_ui_handler.send_message_regen(regen_msg)