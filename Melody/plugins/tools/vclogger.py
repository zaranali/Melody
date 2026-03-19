"""
VC Logger - Melody Music Bot
Logs voice chat join/leave events with smart polling and flood-wait handling.
"""

import asyncio
import re
import random
from logging import getLogger
from typing import Dict, Set

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.raw import functions

from Melody import app
from Melody.utils.database import get_assistant
from Melody.utils.formatters import to_small_caps
from Melody.utils.permissions import adminsOnly
from Melody.core.mongo import mongodb

LOGGER = getLogger(__name__)

# ── In-memory state ────────────────────────────────────────────────────────────
vc_active_users: Dict[int, Set[int]] = {}   # chat_id → set of user_ids currently in VC
active_vc_chats: Set[int] = set()           # chats being actively monitored
vc_logging_status: Dict[int, bool] = {}     # chat_id → enabled/disabled
_monitor_locks: Set[int] = set()            # guard against duplicate monitor tasks

vcloggerdb = mongodb.vclogger



# ── DB helpers ─────────────────────────────────────────────────────────────────

async def load_vc_logger_status():
    """Load all per-chat logging statuses from DB and start monitors for enabled chats."""
    try:
        enabled = []
        async for doc in vcloggerdb.find({}):
            cid, status = doc["chat_id"], doc["status"]
            vc_logging_status[cid] = status
            if status:
                enabled.append(cid)
        for cid in enabled:
            asyncio.create_task(check_and_monitor_vc(cid))
        LOGGER.info(f"VC logger: loaded {len(vc_logging_status)} chats, {len(enabled)} enabled")
    except Exception as e:
        LOGGER.error(f"VC logger load error: {e}")


async def save_vc_logger_status(chat_id: int, status: bool):
    try:
        await vcloggerdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"chat_id": chat_id, "status": status}},
            upsert=True,
        )
    except Exception as e:
        LOGGER.error(f"VC logger save error [{chat_id}]: {e}")


async def get_vc_logger_status(chat_id: int) -> bool:
    if chat_id in vc_logging_status:
        return vc_logging_status[chat_id]
    try:
        doc = await vcloggerdb.find_one({"chat_id": chat_id})
        status = doc["status"] if doc else False
        vc_logging_status[chat_id] = status
        return status
    except Exception as e:
        LOGGER.error(f"VC logger get error [{chat_id}]: {e}")
        return False


# ── Command handler ────────────────────────────────────────────────────────────

@app.on_message(filters.command("vclogger", prefixes=[".", "!", "/", "?", "'"]) & filters.group)
@adminsOnly("can_manage_video_chats")
async def vclogger_command(_, message: Message):
    chat_id = message.chat.id
    args = message.text.split()
    status = await get_vc_logger_status(chat_id)
    state_label = to_small_caps("Enabled" if status else "Disabled")

    if len(args) == 1:
        return await message.reply(
            f"📌 <b>VC Logging Status:</b> <b>{state_label}</b>\n"
            f"Use <code>/vclogger on</code> or <code>/vclogger off</code>",
            disable_web_page_preview=True,
        )

    arg = args[1].lower()
    if arg in ("on", "enable", "yes"):
        vc_logging_status[chat_id] = True
        await save_vc_logger_status(chat_id, True)
        await message.reply("✅ <b>VC logging enabled.</b>", disable_web_page_preview=True)
        asyncio.create_task(check_and_monitor_vc(chat_id))

    elif arg in ("off", "disable", "no"):
        vc_logging_status[chat_id] = False
        await save_vc_logger_status(chat_id, False)
        active_vc_chats.discard(chat_id)
        vc_active_users.pop(chat_id, None)
        await message.reply("🚫 <b>VC logging disabled.</b>", disable_web_page_preview=True)

    else:
        await message.reply(
            "❌ <b>Unknown option.</b> Use <code>on</code> or <code>off</code>.",
            disable_web_page_preview=True,
        )


# ── Participant fetcher with safe flood-wait ───────────────────────────────────

_FLOOD_RE = re.compile(r"FLOOD_WAIT_(\d+)")
_CALL_NOT_FOUND = {"GROUPCALL_NOT_FOUND", "CALL_NOT_FOUND", "NO_GROUPCALL"}
_MAX_FLOOD_RETRIES = 2


async def get_group_call_participants(userbot, peer, *, _retry: int = 0):
    try:
        full = await userbot.invoke(functions.channels.GetFullChannel(channel=peer))
        if not getattr(full.full_chat, "call", None):
            return []
        call = full.full_chat.call
        result = await userbot.invoke(
            functions.phone.GetGroupParticipants(
                call=call, ids=[], sources=[], offset="", limit=500
            )
        )
        return result.participants
    except Exception as e:
        msg = str(e).upper()
        m = _FLOOD_RE.search(msg)
        if m and _retry < _MAX_FLOOD_RETRIES:
            wait = int(m.group(1)) + 1
            LOGGER.warning(f"VC logger flood wait {wait}s (retry {_retry + 1})")
            await asyncio.sleep(wait)
            return await get_group_call_participants(userbot, peer, _retry=_retry + 1)
        if any(err in msg for err in _CALL_NOT_FOUND):
            return []
        LOGGER.error(f"VC logger get_participants error: {e}")
        return []


# ── Monitor loop ───────────────────────────────────────────────────────────────

async def monitor_vc_chat(chat_id: int):
    """Poll VC participants every 5 seconds and emit join/leave events."""
    userbot = await get_assistant(chat_id)
    if not userbot:
        _monitor_locks.discard(chat_id)
        return

    LOGGER.info(f"VC logger: started monitoring chat {chat_id}")
    try:
        while chat_id in active_vc_chats and await get_vc_logger_status(chat_id):
            try:
                peer = await userbot.resolve_peer(chat_id)
                participants = await get_group_call_participants(userbot, peer)
                new_users = {
                    p.peer.user_id
                    for p in participants
                    if hasattr(p, "peer") and hasattr(p.peer, "user_id")
                }
                current_users = vc_active_users.get(chat_id, set())

                joined = new_users - current_users
                left = current_users - new_users

                tasks = (
                    [handle_user_join(chat_id, uid, userbot) for uid in joined]
                    + [handle_user_leave(chat_id, uid, userbot) for uid in left]
                )
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

                vc_active_users[chat_id] = new_users

            except Exception as e:
                LOGGER.error(f"VC monitor error [{chat_id}]: {e}")

            await asyncio.sleep(5)
    finally:
        _monitor_locks.discard(chat_id)
        active_vc_chats.discard(chat_id)
        LOGGER.info(f"VC logger: stopped monitoring chat {chat_id}")


async def check_and_monitor_vc(chat_id: int):
    """Start monitor task for chat_id if not already running."""
    if not await get_vc_logger_status(chat_id):
        return
    if not await get_assistant(chat_id):
        return
    if chat_id in _monitor_locks:
        return  # Already running — prevent duplicate tasks
    _monitor_locks.add(chat_id)
    active_vc_chats.add(chat_id)
    asyncio.create_task(monitor_vc_chat(chat_id))


# ── Join / Leave message handlers ──────────────────────────────────────────────

_JOIN_MSGS = [
    "🎤 {mention} <b>ᴊᴜsᴛ ᴊᴏɪɴᴇᴅ ᴛʜᴇ ᴠᴄ – ʟᴇᴛ's ᴍᴀᴋᴇ ɪᴛ ʟɪᴠᴇʟʏ! 🎶</b>",
    "✨ {mention} <b>ɪs ɴᴏᴡ ɪɴ ᴛʜᴇ ᴠᴄ – ᴡᴇʟᴄᴏᴍᴇ ᴀʙᴏᴀʀᴅ! 💫</b>",
    "🎵 {mention} <b>ʜᴀs ᴊᴏɪɴᴇᴅ – ʟᴇᴛ's ʀᴏᴄᴋ ᴛʜɪs ᴠɪʙᴇ! 🔥</b>",
    "🌊 {mention} <b>ᴅʀᴏᴘᴘᴇᴅ ɪɴᴛᴏ ᴛʜᴇ ᴠᴄ – ɢᴏ sᴀʏ ʜɪ! 👋</b>",
]

_LEAVE_MSGS = [
    "👋 {mention} <b>ʟᴇғᴛ ᴛʜᴇ ᴠᴄ – ʜᴏᴘᴇ ᴛᴏ sᴇᴇ ʏᴏᴜ ʙᴀᴄᴋ sᴏᴏɴ! 🌟</b>",
    "🚪 {mention} <b>sᴛᴇᴘᴘᴇᴅ ᴏᴜᴛ – ᴡᴇ'ʟʟ ᴍɪss ʏᴏᴜ! 💖</b>",
    "✌️ {mention} <b>sᴀɪᴅ ɢᴏᴏᴅʙʏᴇ – ᴄᴏᴍᴇ ʙᴀᴄᴋ ᴀɴᴅ ᴊᴏɪɴ ᴛʜᴇ ғᴜɴ! 🎶</b>",
    "🌙 {mention} <b>ʜᴀs ʟᴇғᴛ ᴛʜᴇ ᴄʜᴀᴛ – ᴜɴᴛɪʟ ɴᴇxᴛ ᴛɪᴍᴇ! 🎵</b>",
]


def _make_mention(user) -> str:
    name = to_small_caps(user.first_name or "Someone")
    return f'<a href="tg://user?id={user.id}"><b>{name}</b></a>'


async def _send_and_delete(chat_id: int, text: str, delay: int = 60):
    try:
        msg = await app.send_message(chat_id, text)
        await asyncio.sleep(delay)
        await msg.delete()
    except Exception:
        pass


async def handle_user_join(chat_id: int, user_id: int, userbot):
    try:
        user = await userbot.get_users(user_id)
        mention = _make_mention(user)
        text = random.choice(_JOIN_MSGS).format(mention=mention)
        asyncio.create_task(_send_and_delete(chat_id, text))
    except Exception as e:
        LOGGER.error(f"VC join msg error [{user_id}]: {e}")


async def handle_user_leave(chat_id: int, user_id: int, userbot):
    try:
        user = await userbot.get_users(user_id)
        mention = _make_mention(user)
        text = random.choice(_LEAVE_MSGS).format(mention=mention)
        asyncio.create_task(_send_and_delete(chat_id, text))
    except Exception as e:
        LOGGER.error(f"VC leave msg error [{user_id}]: {e}")


# ── Startup initializer ────────────────────────────────────────────────────────

async def initialize_vc_logger():
    await load_vc_logger_status()


__MODULE__ = "ᴠᴄ ʟᴏɢɢᴇʀ"
__HELP__ = """
<b>VC Logger:</b>
Announce when users join or leave the voice chat.

• <code>/vclogger on</code> — Enable join/leave messages
• <code>/vclogger off</code> — Disable logging
• <code>/vclogger</code> — Check current status

<i>Requires <b>Manage Video Chats</b> permission.</i>
"""
