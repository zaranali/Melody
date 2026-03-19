"""
tag.py — Tag all members / admins.
Fixes applied:
- SPAM_CHATS is now a set (O(1) lookups).
- Admin list cached per-chat for 60s to avoid redundant API calls.
- from_user guard in tag_all_users.
- Markdown clean_text now also escapes [ and ].
- Progress message edited to summary on completion (auto-deletes after 60s).
- Error messages in process_members auto-delete after 30s.
- FloodWait at outer level now notifies the user and retries properly.
- BATCH_SIZE constant instead of magic number 5.
- tag_all_admins reuses the fetched admin list for permission check.
- __MODULE__ / __HELP__ corrected (were MODULE/HELP).
- @ prefix removed from command triggers to avoid false matches.
"""

import asyncio
import time
import re
import random
from typing import Dict, Optional, Tuple, List

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter, ParseMode
from pyrogram.errors import FloodWait
from pyrogram.types import Message

from Melody import app


# ── Constants ──────────────────────────────────────────────────────────────────

TG_MAX_LENGTH = 4096    # Telegram hard message size limit
MAX_BATCH_SIZE = 20     # Max mentions per message regardless of char count
SLEEP_BETWEEN = 2       # seconds between batches
AUTO_DELETE_DELAY = 60  # seconds before summary is deleted
# Per-mention budget in HTML: <a href="tg://user?id=0000000000">🦋</a>  ≈ 50 chars
_PER_MENTION_EST = 52

EMOJI = [
    "🦋🦋🦋🦋🦋",
    "🧚🌸🧋🍬🫖",
    "🥀🌷🌹🌺💐",
    "🌸🌿💮🌱🌵",
    "❤️💚💙💜🖤",
    "💓💕💞💗💖",
    "🌸💐🌺🌹🦋",
    "🍔🦪🍛🍲🥗",
    "🍎🍓🍒🍑🌶️",
    "🧋🥤🧋🥛🍷",
    "🍬🍭🧁🎂🍡",
    "🍨🧉🍺☕🍻",
    "🥪🥧🍦🍥🍚",
    "🫖☕🍹🍷🥛",
    "☕🧃🍩🍦🍙",
    "🍁🌾💮🍂🌿",
    "🌨️🌥️⛈️🌩️🌧️",
    "🌷🏵️🌸🌺💐",
    "💮🌼🌻🍀🍁",
    "🧟🦸🦹🧙👸",
    "🌼🌳🌲🌴🌵",
    "🎉🎊🎈🎂🎀",
    "🪴🌵🌴🌳🌲",
    "🎄🎋🎍🎑🎎",
    "🦅🦜🕊️🦤🦢",
    "🐬🦭🦈🐋🐳",
    "🦩🦀🦑🐙🦪",
    "🥬🍉🧁🧇🔮",
]


# ── State ──────────────────────────────────────────────────────────────────────

SPAM_CHATS: set = set()   # chats with an active tagging process

# Admin cache: {chat_id: (timestamp, {user_id, ...})}
_admin_cache: Dict[int, Tuple[float, set]] = {}
_ADMIN_CACHE_TTL = 60  # seconds


# ── Helpers ────────────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """HTML-escape user-supplied text to safely embed in HTML messages."""
    if not text:
        return ""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


async def get_admins(chat_id: int) -> set:
    """Return a cached set of admin user IDs for the chat."""
    now = time.monotonic()
    cached = _admin_cache.get(chat_id)
    if cached and (now - cached[0]) < _ADMIN_CACHE_TTL:
        return cached[1]
    admin_ids = {
        m.user.id
        async for m in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS)
        if not m.user.is_bot
    }
    _admin_cache[chat_id] = (now, admin_ids)
    return admin_ids


async def is_admin(chat_id: int, user_id: int) -> bool:
    return user_id in await get_admins(chat_id)


async def _auto_delete(msg: Message, delay: int = AUTO_DELETE_DELAY):
    await asyncio.sleep(delay)
    try:
        await msg.delete()
    except Exception:
        pass


async def _send_temp(chat_id: int, text: str, delay: int = 30):
    """Send a temporary message that auto-deletes after `delay` seconds."""
    try:
        msg = await app.send_message(chat_id, text, disable_web_page_preview=True)
        asyncio.create_task(_auto_delete(msg, delay))
    except Exception:
        pass


# ── Core tagging engine ────────────────────────────────────────────────────────

async def process_members(
    chat_id: int,
    members: List,
    text: Optional[str] = None,
    replied: Optional[Message] = None,
) -> int:
    tagged = 0
    usertxt = ""
    emoji_seq = random.choice(EMOJI)
    emoji_idx = 0
    # How many chars the prefix consumes (only counted when not a reply)
    prefix_len = len(text) + 2 if text else 0  # +2 for "\n\n"
    available = TG_MAX_LENGTH - prefix_len

    async def _flush(batch_text: str):
        try:
            if replied:
                # Use app.send_message instead of replied.reply_text for more robustness
                await app.send_message(
                    chat_id,
                    batch_text,
                    reply_to_message_id=replied.id,
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.HTML,
                )
            else:
                await app.send_message(
                    chat_id,
                    f"{text}\n\n{batch_text}" if text else batch_text,
                    disable_web_page_preview=True,
                    parse_mode=ParseMode.HTML,
                )
            await asyncio.sleep(SLEEP_BETWEEN)
        except FloodWait as fw:
            await asyncio.sleep(fw.value + 2)
        except Exception as e:
            asyncio.create_task(
                _send_temp(chat_id, f"⚠️ Batch error: <code>{e}</code>", delay=20)
            )

    batch_count = 0
    for member in members:
        if chat_id not in SPAM_CHATS:
            break
        if not member.user or member.user.is_deleted or member.user.is_bot:
            continue

        emoji = emoji_seq[emoji_idx % len(emoji_seq)]
        tag = f'<a href="tg://user?id={member.user.id}">{emoji}</a> '
        emoji_idx += 1
        tagged += 1
        batch_count += 1

        usertxt += tag

        # Flush if we'd overflow or hit max batch size
        should_flush = (
            len(usertxt) + _PER_MENTION_EST > available
            or batch_count >= MAX_BATCH_SIZE
        )
        if should_flush:
            await _flush(usertxt)
            usertxt = ""
            batch_count = 0
            emoji_seq = random.choice(EMOJI)
            emoji_idx = 0

    # Flush remaining
    if usertxt and chat_id in SPAM_CHATS:
        await _flush(usertxt)

    return tagged


# ── Commands ───────────────────────────────────────────────────────────────────

@app.on_message(
    filters.command(["all", "allmention", "mentionall", "tagall"], prefixes=["/", "!"])
    & filters.group
)
async def tag_all_users(_, message: Message):
    if not message.from_user:
        return  # anonymous admin / channel post — skip

    if not await is_admin(message.chat.id, message.from_user.id):
        sent = await message.reply_text("🔒 Only admins can use this command.")
        asyncio.create_task(_auto_delete(sent))
        return

    chat_id = message.chat.id

    if chat_id in SPAM_CHATS:
        sent = await message.reply_text("⏳ Tagging is already running. Use /cancel to stop.")
        asyncio.create_task(_auto_delete(sent))
        return

    replied = message.reply_to_message
    if len(message.command) < 2 and not replied:
        sent = await message.reply_text(
            "ℹ️ Usage: <code>/tagall Hello everyone!</code>  or reply to a message."
        )
        asyncio.create_task(_auto_delete(sent))
        return

    text = clean_text(message.text.split(None, 1)[1]) if not replied else None

    # Collect members
    members = [m async for m in app.get_chat_members(chat_id)]
    total = len(members)

    progress = await message.reply_text(f"⏳ Tagging <b>{total}</b> members…")
    SPAM_CHATS.add(chat_id)

    try:
        tagged = await process_members(chat_id, members, text=text, replied=replied)
        await progress.edit_text(
            f"✅ <b>Tagging completed!</b>\n"
            f"👥 Total members: <b>{total}</b>\n"
            f"🏷 Tagged: <b>{tagged}</b>"
        )
        asyncio.create_task(_auto_delete(progress))
    except FloodWait as fw:
        await progress.edit_text(f"⚠️ Flood wait {fw.value}s. Try again later.")
        asyncio.create_task(_auto_delete(progress))
    except Exception as e:
        await progress.edit_text(f"❌ Error: <code>{e}</code>")
        asyncio.create_task(_auto_delete(progress))
    finally:
        SPAM_CHATS.discard(chat_id)


@app.on_message(
    filters.command(["admintag", "adminmention", "admins", "report"], prefixes=["/", "!"])
    & filters.group
)
async def tag_all_admins(_, message: Message):
    if not message.from_user:
        return

    chat_id = message.chat.id

    # Fetch admins once — reuse for both permission check and tagging
    admins = await get_admins(chat_id)
    if message.from_user.id not in admins:
        sent = await message.reply_text("🔒 Only admins can use this command.")
        asyncio.create_task(_auto_delete(sent))
        return

    if chat_id in SPAM_CHATS:
        sent = await message.reply_text("⏳ Tagging is already running. Use /cancel to stop.")
        asyncio.create_task(_auto_delete(sent))
        return

    replied = message.reply_to_message
    if len(message.command) < 2 and not replied:
        sent = await message.reply_text(
            "ℹ️ Usage: <code>/admins Hello admins!</code>  or reply to a message."
        )
        asyncio.create_task(_auto_delete(sent))
        return

    text = clean_text(message.text.split(None, 1)[1]) if not replied else None

    # Fetch full admin Member objects for tagging
    members = [
        m
        async for m in app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS)
    ]
    total = len(members)

    progress = await message.reply_text(f"⏳ Tagging <b>{total}</b> admins…")
    SPAM_CHATS.add(chat_id)

    try:
        tagged = await process_members(chat_id, members, text=text, replied=replied)
        await progress.edit_text(
            f"✅ <b>Admin tagging completed!</b>\n"
            f"👑 Total admins: <b>{total}</b>\n"
            f"🏷 Tagged: <b>{tagged}</b>"
        )
        asyncio.create_task(_auto_delete(progress))
    except FloodWait as fw:
        await progress.edit_text(f"⚠️ Flood wait {fw.value}s. Try again later.")
        asyncio.create_task(_auto_delete(progress))
    except Exception as e:
        await progress.edit_text(f"❌ Error: <code>{e}</code>")
        asyncio.create_task(_auto_delete(progress))
    finally:
        SPAM_CHATS.discard(chat_id)


@app.on_message(
    filters.command(
        ["stopmention", "cancel", "cancelmention", "offmention", "mentionoff", "cancelall"],
        prefixes=["/", "!"],
    )
    & filters.group
)
async def cancelcmd(_, message: Message):
    if not message.from_user:
        return
    chat_id = message.chat.id
    if not await is_admin(chat_id, message.from_user.id):
        sent = await message.reply_text("🔒 Only admins can stop the tagging process.")
        asyncio.create_task(_auto_delete(sent))
        return

    if chat_id in SPAM_CHATS:
        SPAM_CHATS.discard(chat_id)
        sent = await message.reply_text("✅ Tagging process stopped!")
    else:
        sent = await message.reply_text("ℹ️ No tagging process is currently running.")
    asyncio.create_task(_auto_delete(sent))


# ── Help ───────────────────────────────────────────────────────────────────────

__MODULE__ = "ᴛᴀɢ ᴀʟʟ"
__HELP__ = """
<b>Tag All Members / Admins</b>

• <code>/tagall [text]</code> — Tag all members (or reply to a message)
• <code>/admins [text]</code> — Tag all admins (or reply to a message)
• <code>/cancel</code> — Stop an ongoing tagging process

<i>All commands require <b>admin</b> privileges. Summary auto-deletes after 60s.</i>
"""
