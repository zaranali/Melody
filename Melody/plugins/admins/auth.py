from pyrogram import filters
from pyrogram.types import Message
from Melody import app
from Melody.utils import extract_user, int_to_alpha
from Melody.utils.database import (
    delete_authuser,
    get_authuser,
    get_authuser_names,
    save_authuser,
)
from Melody.utils.decorators import AdminActual, language
from Melody.utils.inline import close_markup
from config import BANNED_USERS, adminlist

"""
Authorization management for group chats.
Allows admins to authorize specific users to use bot admin commands
without being actual group administrators.
"""

@app.on_message(filters.command("auth") & filters.group & ~BANNED_USERS)
@AdminActual
async def auth(client, message: Message, _):
    """Authorizes a user to use bot admin commands."""
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])

    user = await extract_user(message)
    token = await int_to_alpha(user.id)
    _check = await get_authuser_names(message.chat.id)

    # Limit authorization to 25 users per group
    if len(_check) >= 25:
        return await message.reply_text(_["auth_1"])

    if token not in _check:
        auth_data = {
            "auth_user_id": user.id,
            "auth_name": user.first_name,
            "admin_id": message.from_user.id,
            "admin_name": message.from_user.first_name,
        }

        # Update local admin cache
        cached_admins = adminlist.get(message.chat.id)
        if cached_admins and user.id not in cached_admins:
            cached_admins.append(user.id)

        await save_authuser(message.chat.id, token, auth_data)
        return await message.reply_text(_["auth_2"].format(user.mention))
    else:
        return await message.reply_text(_["auth_3"].format(user.mention))

@app.on_message(filters.command("unauth") & filters.group & ~BANNED_USERS)
@AdminActual
async def unauth(client, message: Message, _):
    """De-authorizes a user from using bot admin commands."""
    if not message.reply_to_message and len(message.command) != 2:
        return await message.reply_text(_["general_1"])

    user = await extract_user(message)
    token = await int_to_alpha(user.id)
    deleted = await delete_authuser(message.chat.id, token)

    # Update local admin cache
    cached_admins = adminlist.get(message.chat.id)
    if cached_admins and user.id in cached_admins:
        cached_admins.remove(user.id)

    if deleted:
        return await message.reply_text(_["auth_4"].format(user.mention))
    else:
        return await message.reply_text(_["auth_5"].format(user.mention))

@app.on_message(filters.command(["authlist", "authusers"]) & filters.group & ~BANNED_USERS)
@language
async def authusers(client, message: Message, _):
    """Lists all authorized users in the current group."""
    auth_tokens = await get_authuser_names(message.chat.id)
    if not auth_tokens:
        return await message.reply_text(_["setting_4"])

    mystic = await message.reply_text(_["auth_6"])
    response_text = _["auth_7"].format(message.chat.title)

    count = 0
    for token in auth_tokens:
        data = await get_authuser(message.chat.id, token)
        user_id = data["auth_user_id"]
        admin_id = data["admin_id"]
        admin_name = data["admin_name"]

        try:
            user = await app.get_users(user_id)
            user_name = user.first_name
            count += 1
            response_text += f"{count}➤ {user_name} [<code>{user_id}</code>]\n"
            response_text += f"   {_['auth_8']} {admin_name} [<code>{admin_id}</code>]\n\n"
        except Exception:
            continue

    await mystic.edit_text(response_text, reply_markup=close_markup(_))
