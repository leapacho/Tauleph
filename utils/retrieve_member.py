from discord import Message, Interaction, Member
from typing import Union


async def retrieve_member(discord_object: Union[Message, Interaction], member_id) -> Member:
    member = discord_object.guild.get_member(member_id)
    if member is None:
        member = await discord_object.guild.fetch_member(member_id)
    return member