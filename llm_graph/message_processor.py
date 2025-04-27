from bot.discord_obj_processor import discord_obj
from config.config import config
from google import genai
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
import ffmpy
import aiohttp
import asyncio
import tempfile
import os

class MessageProcessor:
    """
    Manages the processing of messages. 

    Serves like the bridge between Discord and Groq's API.
    """
    def __init__(self):
        self.message_template = f"{discord_obj.message_author} sent a message. Respond to it in a conversational manner: {discord_obj.message_content}"
        self.sys_prompt = ""
        self.downloaded_attachment = None

    async def process_message(self) -> str:
        """
        Processes the given message. 

        Can process images, audio and text, and then sends the output.
        """

        self.sys_prompt = await config.initialize_system_prompt()

        processing_methods={ # This dictionary allows for easy implementation of other processing methods.
            "image": self._process_image,
            "audio": self._process_audio,
            "video": self._process_video,
            "gif": self._process_gif, # This dict entry isn't used, but the method is.
            "": self._process_text # If att_type is empty then this is the default.
        }
        


        self.downloaded_attachment = await self._download_attachment(discord_obj.att_url)
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
        if discord_obj.message_content.startswith("https://") and discord_obj.message_content.endswith(".gif"):
            result = await self._process_gif()
            return result
        if discord_obj.message_content.startswith("https://tenor.com/") and "gif" in discord_obj.message_content:
            result = await self._process_gif()
            return result
        for prefix, method in processing_methods.items():
            if discord_obj.att_type.startswith(prefix):
                result = await method() # Calls the corresponding method.
                return result
            
    async def _download_attachment(self, url: str):
        if url:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if "discordapp" in url:
                        content_type = response.headers.get('Content-Type', '')
                        # Check if the response is actually media and not HTML
                        text_content = ""
                        if 'text/plain' in content_type and response.status == 404: # Check if the response has a text response.
                            text_content = await response.text()
                            if "This content is no longer available." in text_content: # Check if the response is this string.

                                # Fix the URL using hyonsu's API.
                                if "cdn.discordapp.com" in url:
                                    alt_url = url.replace("cdn.discordapp.com", "fixcdn.hyonsu.com")
                                elif "media.discordapp.net" in url:
                                    alt_url = url.replace("media.discordapp.net", "fixcdn.hyonsu.com")
                                else:
                                    raise NotImplementedError(f"Discord CDN not implemented: {url}")
                                print(alt_url)
                                # Get a response from the alternate URL.
                                async with session.get(alt_url) as alt_response:
                                    return await alt_response.read()
                        elif response.status == 200:
                            return await response.read()
                        else:
                            response.raise_for_status()
                    elif "tenor" in url:
                        soup = BeautifulSoup(await response.text(), 'html.parser')
                        media_url = None
                        og_image_meta = soup.find('meta', property='og:image')

                        if og_image_meta and og_image_meta.get('content'):
                            media_url = og_image_meta['content']
                        async with aiohttp.ClientSession() as session:
                            async with session.get(media_url) as response:
                                return await response.read()

    async def _process_image(self) -> str:
        """
        Processes the image.

        Returns:
            str: The output of the LLM's processing of the image.
        """
        async with discord_obj.message.channel.typing():
            image_messages=([
                {"type": "text", "text": self.message_template},
                {"type": "image_url", "image_url": discord_obj.att_url}
                ], 
                self.sys_prompt)
        return image_messages

    async def _process_audio(self) -> str:
        """
        Processes the audio.

        Returns:
            str: The output of the LLM's processing of the image.
        """
        myfile = await self._upload_to_files_api(self.downloaded_attachment)

        async with discord_obj.message.channel.typing():
            audio_messages=([{"type": "text", "text": self.message_template},
                            {"type": "media", "mime_type": discord_obj.att_type, "file_uri": myfile.uri}],
                            self.sys_prompt)
        return audio_messages

    async def _process_text(self) -> str:
        """
        Processes the text given.

        Returns:
            str: The output of the LLM's processing of the text.
        """
        async with discord_obj.message.channel.typing():
                text_messages=([{
                    "type": "text",
                    "text": self.message_template
                }], 
                self.sys_prompt) # These lines made me rewrite the entirety of Tauleph one time.
        return text_messages
    
    async def _process_video(self) -> str:
        """
        Process the video given.

        Returns:
            str: The processed video.
        """

        myfile = self._upload_to_files_api(self.downloaded_attachment)
        

        async with discord_obj.message.channel.typing():
            video_messages=([{"type": "text", "text": self.message_template},
                            {"type": "media", "mime_type": discord_obj.att_type, "file_uri": myfile.uri}],
                            f"{self.sys_prompt}. The user {discord_obj.message_author} sent a video.")
        return video_messages
    
    async def _process_gif(self) -> tuple:
        # Get the downloaded gif.
        self.downloaded_attachment = await self._download_attachment(discord_obj.message_content)

        # Conversion: gif -> mp4
        with ThreadPoolExecutor() as pool:
            mp4_content = await asyncio.get_event_loop().run_in_executor(
                pool,
                lambda: self.convert_gif_to_mp4(self.downloaded_attachment)
            )
            media_content = mp4_content
    
        myfile = await self._upload_to_files_api(media_content, gif=True)
        # Return the processed message.
        async with discord_obj.message.channel.typing():
            gif_messages=([{"type": "text", "text": f""},
                            {"type": "media", "mime_type": "video/mp4", "file_uri": myfile.uri}],
                            f"{self.sys_prompt}. The user {discord_obj.message_author} sent a GIF in the form of a video.")
        return gif_messages
    
    def convert_gif_to_mp4(self, content_bytes):
        """
        Synchronously converts gif bytes to MP4.
        """
        
        with tempfile.NamedTemporaryFile(suffix=".gif", delete=False) as temp_input:
            temp_input.write(content_bytes)
            temp_input_path = temp_input.name

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp_output:
            temp_output_path = temp_output.name

        try:
            ff = ffmpy.FFmpeg(
                inputs={temp_input_path: "-f gif"},
                outputs={temp_output_path: '-y'}
            )            
            # Execute the conversion
            ff.run()

            with open(temp_output_path, "rb") as file:
                output_bytes = file.read()
            return  output_bytes
        except Exception as e:
            print(f"Error during conversion: {e}")
            return None
        finally:
            if os.path.exists(temp_input_path):
                os.unlink(temp_input_path)
            if os.path.exists(temp_output_path):
                os.unlink(temp_output_path)

    async def _upload_to_files_api(self, media_content, gif: bool = False):
        file_data = BytesIO(media_content)
        client = genai.Client()
                # Upload to the Files API.
        mime_type = discord_obj.att_type if not gif else "video/mp4"
        myfile = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.files.upload(file=file_data, config={"mime_type": mime_type})
        )
        # Wait for processing.
        while myfile.state.name == "PROCESSING":
            print("processing video...")
            await asyncio.sleep(5)
            myfile = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: client.files.get(name=myfile.name)
        )
        return myfile