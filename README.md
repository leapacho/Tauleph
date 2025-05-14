# Tauleph
A simple Discord AI bot written in Python, using Discord.py, Gemini, LangChain and LangGraph.

![tauleph_githubimage png](https://github.com/user-attachments/assets/75bd1f24-d125-430d-a587-0983a91394cc)


WARNING: THIS IS MY FIRST PYTHON PROJECT AND GITHUB REPOSITORY!!! THE CODE IS NOT GUARANTEED TO WORK AS INTENDED!!!
Constructive criticism, feedback and contributions are welcome! Please consider making a pull request for your fork as it is likely I'll accept the changes! (but first read the [contribution rules](https://github.com/leapacho/Tauleph/blob/main/CONTRIBUTING.md))
You are also open to make an [issue](https://github.com/leapacho/Tauleph/issues/new). I will try my best to maintain this repo.

You can test Tauleph in its [testing Discord server](https://discord.gg/CrXuXNfvHV) (the bot is very possibly not active).

For anything about Tauleph, you can send me a DM in Discord. My Discord username: limonero. (with the dot)

#  Functionality
##  Regeneration:
To regenerate Tauleph's messages, you can click to one of the following buttons. The repeat button (🔁) makes a new regeneration, while the arrow buttons (⬅➡️) allow you to navigate between previous regenerations.
##  Invoking:
To invoke Tauleph, you can do one of two things: type its name in your message or reply to one of Tauleph's messages. Example: 'Tauleph, what is Eggs Benedict?' You don't have to include Tauleph's name in your message if you reply to one of its messages.
##  Changing Tauleph's name:
You can customize the name it responds to by simply changing Tauleph's server nickname to your liking.
##  Audios, images, videos and gifs:
Tauleph can see and hear any images or audio you send it. Just invoke it like you normally would, and it will reply accordingly. You can also speak to it using voice messages by first replying to one of its messages and then sending the voice message. It supports videos and gifs from Discord and Tenor.
##  Web search:
Tauleph can autonomously search the internet using the SearXNG search engine. This extends its knowledge and usefulness. An example of how useful this is to query it about a recent event, and you'll see it respond with accurate, up-to-date information.

#  Commands
##  `/select_model:`
This command is used to switch the LLM's model. Currently, there are 11 available Gemini and Gemma models.
##  `/change_system_message:`
This command allows you to change the LLM's system message, AKA, its instructions. For example, you can set the system message to 'You are an angsty teen.' and the LLM will try its best to mimic an angsty teen. As of now, if you don't include Tauleph's server nickname in the system message, 'Your name is [insert nickname here]' will be added at the end of it.
##  `/current_system_message:`
This command will send a message containing the current system message.
##  `/allow_channel:`
This command adds the current channel to the list of channels in which Tauleph can respond.  
## `/disallow_channel:`
This command removes the current channel from the list of channels in which Tauleph can respond.
## `/restore_system_message:`
This command allows you to restore the system message to its default. Use this in cases where the bot is responding strangely or if you've accidentally changed the system message.
## `/clear_memory:`
This clears Tauleph's chat history, or its memory, permanently. You cannot undo this command. Use with caution.
## `/set_settings_to_default:`
This command sets all of Tauleph's configurable settings to their respective defaults.  
## `/set_role:`
Specify which users are allowed to change Tauleph's sensitive settings. You need administrative permissions to use this command.
## `/help functionality:`
Shows the functionality written above.
## `/help commands:`
Shows these commands minus Quickstart and the help command itself.
## `/help quickstart:`
Shows a quickstart of how to do basic configuration on the bot.
