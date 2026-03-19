from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus, ChatType
from pyrogram.types import Message
from pyrogram.errors import ChatAdminRequired, UserNotParticipant, ChatWriteForbidden

from Melody import app
from Melody.utils.database import set_cmode, get_cmode, get_assistant
from Melody.utils.decorators.admins import AdminActual
from config import BANNED_USERS

@app.on_message(filters.command(["channelplay"]) & filters.group & ~BANNED_USERS)
@AdminActual
async def channelplay_command(client, message: Message, _):
    if len(message.command) < 2:
        cmode = await get_cmode(message.chat.id)
        if cmode:
            try:
                chat = await app.get_chat(cmode)
                title = chat.title
            except Exception:
                title = "Unknown Channel"
        else:
            title = "None"
        return await message.reply_text(_["cplay_1"].format(title))
    
    query = message.text.split(None, 1)[1].lower().strip()
    
    if query == "disable":
        await set_cmode(message.chat.id, None)
        return await message.reply_text(_["cplay_7"])
    
    if query == "linked":
        chat = await app.get_chat(message.chat.id)
        if chat.linked_chat:
            await set_cmode(message.chat.id, chat.linked_chat.id)
            return await message.reply_text(
                _["cplay_3"].format(chat.linked_chat.title, chat.linked_chat.id)
            )
        else:
            return await message.reply_text(_["cplay_2"])
    
    if query.startswith("-100"):
        try:
            query = int(query)
        except ValueError:
            pass

    try:
        chat = await app.get_chat(query)
    except Exception as e:
        return await message.reply_text(_["cplay_4"])
        
    if chat.type != ChatType.CHANNEL:
        return await message.reply_text(_["cplay_5"])

    try:
        # Check bot's status in channel
        bot_member = await app.get_chat_member(chat.id, "me")
        if not (bot_member.privileges and bot_member.privileges.can_invite_users and bot_member.privileges.can_manage_video_chats):
            return await message.reply_text("I need 'Invite Users via Link' and 'Manage Live Streams' permissions in the target channel.")
            
        # Check assistant status in channel
        userbot = await get_assistant(chat.id)
        try:
            assistant_member = await app.get_chat_member(chat.id, userbot.id)
            if assistant_member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
                 return await message.reply_text(f"The assistant account ({userbot.mention}) must be an administrator in the channel with 'Manage Live Streams' permission.")
            if not (assistant_member.privileges and assistant_member.privileges.can_manage_video_chats):
                 return await message.reply_text(f"The assistant account ({userbot.mention}) is missing 'Manage Live Streams' permission in the channel.")
        except UserNotParticipant:
            return await message.reply_text(f"The assistant account ({userbot.mention}) is not a member of the target channel. Please add it as an administrator.")

        # Check user's status in channel
        user_member = await app.get_chat_member(chat.id, message.from_user.id)
        if user_member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
             return await message.reply_text("You need to be an administrator in the target channel to connect it.")
    except UserNotParticipant:
        return await message.reply_text("You are not a member of the target channel.")
    except Exception as e:
        return await message.reply_text(_["cplay_4"])

    await set_cmode(message.chat.id, chat.id)
    return await message.reply_text(_["cplay_3"].format(chat.title, chat.id))
