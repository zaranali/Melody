from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, Message

from Melody import app
from Melody.utils.database import get_playmode, get_playtype, is_nonadmin_chat
from Melody.utils.decorators import language
from Melody.utils.inline.settings import playmode_users_markup
from config import BANNED_USERS

@app.on_message(filters.command(["playmode", "mode"]) & filters.group & ~BANNED_USERS)
@language
async def playmode_(client, message: Message, _):
    playmode = await get_playmode(message.chat.id)
    is_non_admin = await is_nonadmin_chat(message.chat.id)
    playty = await get_playtype(message.chat.id)
    
    buttons = playmode_users_markup(
        _, 
        Direct=True if playmode == "Direct" else False, 
        Group=True if not is_non_admin else False, 
        Playtype=True if playty != "Everyone" else False
    )
    response = await message.reply_text(
        _["play_22"].format(message.chat.title),
        reply_markup=InlineKeyboardMarkup(buttons),
    )
