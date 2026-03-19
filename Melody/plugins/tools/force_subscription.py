import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import (
    ChatAdminRequired,
    UserNotParticipant,
)
from pyrogram.types import (
    CallbackQuery,
    ChatPermissions,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from motor.motor_asyncio import AsyncIOMotorClient

from Melody import app
from Melody.misc import SUDOERS
from config import MONGO_DB_URI

# Use async motor client instead of blocking PyMongo
fsubdb = AsyncIOMotorClient(MONGO_DB_URI)
forcesub_collection = fsubdb.status_db.status

# In-memory cache to prevent spamming the database on every message
FSUB_CACHE = {}

async def load_fsub_cache(chat_id):
    if chat_id in FSUB_CACHE:
        return FSUB_CACHE[chat_id]
    
    # Query database
    data = await forcesub_collection.find_one({"chat_id": chat_id})
    if data:
        FSUB_CACHE[chat_id] = data
    else:
        FSUB_CACHE[chat_id] = None  # None indicates no fsub enabled
    return FSUB_CACHE[chat_id]


@app.on_message(filters.command(["fsub", "forcesub"]) & filters.group)
async def set_forcesub(client: Client, message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    member = await client.get_chat_member(chat_id, user_id)
    # Allow sudoers, group owner, and group admins
    if not (member.status in ["owner", "administrator", "creator"] or user_id in SUDOERS):
        return await message.reply_text("**ᴏɴʟʏ ɢʀᴏᴜᴘ ᴀᴅᴍɪɴs ᴏʀ sᴜᴅᴏᴇʀs ᴄᴀɴ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.**")

    if len(message.command) == 2 and message.command[1].lower() in ["off", "disable"]:
        await forcesub_collection.delete_one({"chat_id": chat_id})
        FSUB_CACHE[chat_id] = None # Clear cache
        return await message.reply_text("**ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.**")

    if len(message.command) != 2:
        return await message.reply_text("**ᴜsᴀɢᴇ: /ғsᴜʙ <ᴄʜᴀɴɴᴇʟ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ> ᴏʀ /ғsᴜʙ ᴏғғ ᴛᴏ ᴅɪsᴀʙʟᴇ**")

    channel_input = message.command[1]

    try:
        channel_info = await client.get_chat(channel_input)
        channel_id = channel_info.id
        channel_username = f"{channel_info.username}" if channel_info.username else None

        fsub_data = {
            "channel_id": channel_id, 
            "channel_username": channel_username
        }

        await forcesub_collection.update_one(
            {"chat_id": chat_id},
            {"$set": fsub_data},
            upsert=True
        )
        
        # Update Cache
        FSUB_CACHE[chat_id] = fsub_data

        await message.reply_text(f"**🎉 ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ sᴇᴛ ᴛᴏ ᴄʜᴀɴɴᴇʟ:** [{channel_info.title}](https://t.me/{channel_username})")

    except Exception as e:
        await message.reply_text("**🚫 ғᴀɪʟᴇᴅ ᴛᴏ sᴇᴛ ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ.** ᴍᴀᴋᴇ sᴜʀᴇ ᴛʜᴇ ʙᴏᴛ ɪs ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ᴛᴀʀɢᴇᴛ ᴄʜᴀɴɴᴇʟ.")

@app.on_chat_member_updated()
async def on_user_join(client: Client, chat_member_updated):
    chat_id = chat_member_updated.chat.id
    user_id = chat_member_updated.from_user.id
    
    forcesub_data = await load_fsub_cache(chat_id)
    if not forcesub_data:
        return  # No force subscription set for this group

    channel_id = forcesub_data["channel_id"]
    channel_username = forcesub_data["channel_username"]

    new_chat_member = chat_member_updated.new_chat_member
    if new_chat_member is None:
        return

    if new_chat_member.status in ["member", "restricted"]:
        try:
            # Check if joining user is in the channel
            await app.get_chat_member(channel_id, user_id)
        except UserNotParticipant:
            # User is not a member of the channel, mute them initially if they join
            try:
                await client.restrict_chat_member(
                    chat_id,
                    user_id,
                    permissions=ChatPermissions(can_send_messages=False)
                )
            except Exception:
                pass


@app.on_callback_query(filters.regex("close_force_sub"))
async def close_force_sub(client: Client, callback_query: CallbackQuery):
    await callback_query.answer("ᴄʟᴏsᴇᴅ!")
    try:
        await callback_query.message.delete()
    except Exception:
        pass


warning_cooldown = {}

async def check_forcesub(client: Client, message: Message):
    chat_id = message.chat.id

    if message.from_user is None:
        return True

    user_id = message.from_user.id
    
    # Check if user is bot owner/sudoer
    if user_id in SUDOERS:
        return True

    forcesub_data = await load_fsub_cache(chat_id)
    if not forcesub_data:
        return True

    # Bypass check if the user is a group admin
    try:
        member = await client.get_chat_member(chat_id, user_id)
        if member.status in ["owner", "administrator", "creator"]:
            return True
    except Exception:
        pass

    channel_id = forcesub_data["channel_id"]
    channel_username = forcesub_data["channel_username"]

    try:
        user_member = await app.get_chat_member(channel_id, user_id)
        if user_member:
            return True
            
    except UserNotParticipant:
        # Actually delete the unauthorized message
        try:
            await message.delete()
        except Exception:
            pass

        # Use a simple cooldown dictionary to prevent spamming warnings if user sends 10 messages quickly
        cooldown_key = f"{chat_id}_{user_id}"
        if cooldown_key in warning_cooldown:
            return False 
        
        warning_cooldown[cooldown_key] = True

        if channel_username:
            channel_url = f"https://t.me/{channel_username}"
        else:
            try:
                invite_link = await app.export_chat_invite_link(channel_id)
                channel_url = invite_link
            except Exception:
                channel_url = "https://t.me/"
                
        warning_msg = await message.reply_photo(
            photo="https://ibb.co/pvp1g9bk",
            caption=(f"**👋 ʜᴇʟʟᴏ {message.from_user.mention},**\n\n**ʏᴏᴜ ᴍᴜsᴛ ᴊᴏɪɴ ᴛʜᴇ [ᴄʜᴀɴɴᴇʟ]({channel_url}) ᴛᴏ ʙᴇ ᴀʟʟᴏᴡᴇᴅ ᴛᴏ sᴇɴᴅ ᴍᴇssᴀɢᴇs ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.**"),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("๏ ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ ๏", url=channel_url)]]),
        )
        
        await asyncio.sleep(10) # 10 second chat cooldown
        try:
            await warning_msg.delete() 
            del warning_cooldown[cooldown_key]
        except Exception:
            pass
            
        return False
        
    except ChatAdminRequired:
        await forcesub_collection.delete_one({"chat_id": chat_id})
        FSUB_CACHE[chat_id] = None
        await message.reply_text("**🚫 ɪ'ᴍ ɴᴏ ʟᴏɴɢᴇʀ ᴀɴ ᴀᴅᴍɪɴ ɪɴ ᴛʜᴇ ғᴏʀᴄᴇᴅ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ᴄʜᴀɴɴᴇʟ. ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ.**")
        return True

@app.on_message(filters.group, group=30)
async def enforce_forcesub(client: Client, message: Message):
    if not await check_forcesub(client, message):
        # Stop propagating further handlers if the user is unauthorized
        message.stop_propagation()

__MODULE__ = "ғsᴜʙ"
__HELP__ = """**
/fsub <ᴄʜᴀɴɴᴇʟ ᴜsᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ> - sᴇᴛ ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.
/fsub off - ᴅɪsᴀʙʟᴇ ғᴏʀᴄᴇ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.**
"""
