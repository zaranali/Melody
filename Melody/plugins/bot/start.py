import time
from pyrogram import filters, StopPropagation
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from py_yt import VideosSearch
import config
from Melody import app
from Melody.misc import _boot_
from Melody.plugins.sudo.sudoers import sudoers_list
from Melody.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from Melody.utils import bot_sys_stats
from Melody.utils.decorators.language import LanguageStart
from Melody.utils.formatters import get_readable_time
from Melody.utils.inline import help_pannel_page1, private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

"""
Start command handler for Melody Bot.
Manages private messages, group interactions, and welcoming new members.
Supports deep-linking for help, sudo list, and track info.
"""

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    """Handles the /start command in private chats."""
    await add_served_user(message.from_user.id)

    # Check for deep-linking parameters (e.g., /start help)
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]

        # Display help menu
        if name.startswith("help"):
            keyboard = help_pannel_page1(_)
            return await message.reply_photo(
                photo=config.START_IMG_URL,
                caption=_["help_1"].format(f"https://t.me/{config.SUPPORT_GROUP}"),
                reply_markup=keyboard,
            )

        # Display sudoers list
        if name.startswith("sud"):
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):  # Optional logging
                await app.send_message(
                    chat_id=config.LOG_GROUP_ID,
                    text=f"{message.from_user.mention} checked the <b>sudolist</b>.\n\n"
                         f"<b>ID:</b> <code>{message.from_user.id}</code>\n"
                         f"<b>User:</b> @{message.from_user.username}",
                )
            return

        # Display detailed track information
        if name.startswith("inf"):
            m = await message.reply_text("🔎")
            video_id = str(name).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={video_id}"

            try:
                results = VideosSearch(query, limit=1)
                result_data = (await results.next()).get("result", [])

                if not result_data:
                    await m.edit_text("❌ No results found.")
                    return

                result = result_data[0]
                searched_text = _["start_6"].format(
                    result["title"], result["duration"], result["viewCount"]["short"],
                    result.get("publishedTime", "Unknown"), result["channel"]["link"],
                    result["channel"]["name"], app.mention
                )

                key = InlineKeyboardMarkup(
                    [[
                        InlineKeyboardButton(text=_["S_B_8"], url=result["link"]),
                        InlineKeyboardButton(text=_["S_B_9"], url=f"https://t.me/{config.SUPPORT_GROUP}"),
                    ]]
                )

                await m.delete()
                await message.reply_photo(
                    photo=result["thumbnails"][0]["url"].split("?")[0],
                    caption=searched_text,
                    reply_markup=key,
                )

                if await is_on_off(2):
                    await app.send_message(
                        chat_id=config.LOG_GROUP_ID,
                        text=f"{message.from_user.mention} checked <b>track info</b> for <code>{video_id}</code>.",
                    )
            except Exception as e:
                await m.edit_text(f"Error fetching info: {e}")
            return

    # Default start message for PM
    out = private_panel(_)
    UP, CPU, RAM, DISK = await bot_sys_stats()
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_2"].format(message.from_user.mention, app.mention, UP, DISK, CPU, RAM),
        reply_markup=InlineKeyboardMarkup(out),
    )
    if await is_on_off(2):
        await app.send_message(
            chat_id=config.LOG_GROUP_ID,
            text=f"{message.from_user.mention} started the bot in PM.",
        )

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    """Handles the /start command in groups."""
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    await message.reply_photo(
        photo=config.START_IMG_URL,
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    await add_served_chat(message.chat.id)

@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    """Welcomes the bot or other users to a chat and performs security checks."""
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)

            # Ban blacklisted users automatically
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except Exception:
                    pass

            # Bot-specific join logic
            if member.id == app.id:
                # Require supergroups
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)

                # Check for blacklisted groups
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            f"https://t.me/{config.SUPPORT_GROUP}",
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                # Send welcome message when bot joins
                out = start_panel(_)
                await message.reply_photo(
                    photo=config.START_IMG_URL,
                    caption=_["start_3"].format(
                        message.from_user.first_name if message.from_user else "Admin",
                        app.mention, message.chat.title, app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
        except StopPropagation:
            raise
        except Exception:
            pass
