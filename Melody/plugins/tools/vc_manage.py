import asyncio
from typing import List, Optional, Union

from pyrogram import Client, filters
from pyrogram.errors import ChatAdminRequired, UserNotParticipant
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.messages import GetFullChat
from pyrogram.raw.functions.phone import CreateGroupCall, DiscardGroupCall, EditGroupCallParticipant
from pyrogram.raw.types import InputGroupCall, InputPeerChannel, InputPeerChat
from pyrogram.types import ChatPrivileges, Message

from Melody import app
from Melody.utils.database import get_assistant, set_loop
from Melody.utils.permissions import adminsOnly


# ── Helpers ───────────────────────────────────────────────────────────────────

_MANAGE_VC_PRIVILEGES = ChatPrivileges(
    can_manage_chat=False,
    can_delete_messages=False,
    can_manage_video_chats=True,
    can_restrict_members=False,
    can_change_info=False,
    can_invite_users=False,
    can_pin_messages=False,
    can_promote_members=False,
)

_REVOKE_PRIVILEGES = ChatPrivileges(
    can_manage_chat=False,
    can_delete_messages=False,
    can_manage_video_chats=False,
    can_restrict_members=False,
    can_change_info=False,
    can_invite_users=False,
    can_pin_messages=False,
    can_promote_members=False,
)


async def auto_delete(message: Message, delay: int = 60):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass


async def _get_assistant_info(chat_id: int):
    """Returns (assistant_client, assistant_user_id) or (None, None) on failure."""
    assistant = await get_assistant(chat_id)
    if assistant is None:
        return None, None
    me = await assistant.get_me()
    return assistant, me.id


async def _grant_vc_manage(chat_id: int, user_id: int):
    """Grant manage_video_chats to the assistant, perform action, then revoke."""
    await app.promote_chat_member(chat_id, user_id, privileges=_MANAGE_VC_PRIVILEGES)


async def _revoke_vc_manage(chat_id: int, user_id: int):
    await app.promote_chat_member(chat_id, user_id, privileges=_REVOKE_PRIVILEGES)


async def get_group_call(
    client: Client, message: Message, err_msg: str = ""
) -> Optional[InputGroupCall]:
    """Resolve the active InputGroupCall for the chat, or None."""
    assistant = await get_assistant(message.chat.id)
    chat_peer = await assistant.resolve_peer(message.chat.id)
    if isinstance(chat_peer, InputPeerChannel):
        full = (await assistant.invoke(GetFullChannel(channel=chat_peer))).full_chat
    elif isinstance(chat_peer, InputPeerChat):
        full = (await assistant.invoke(GetFullChat(chat_id=chat_peer.chat_id))).full_chat
    else:
        sent_msg = await message.reply("<b>❌ Unsupported chat type.</b>")
        asyncio.create_task(auto_delete(sent_msg))
        return None
    if full is not None and full.call:
        return full.call
    sent_msg = await message.reply(f"<b>❌ No active voice chat found.</b> {err_msg}")
    asyncio.create_task(auto_delete(sent_msg))
    return None


# ── VC Start / Stop ────────────────────────────────────────────────────────────

@app.on_message(filters.video_chat_started & filters.group)
async def on_vc_start(_, msg):
    try:
        sent_msg = await msg.reply("<b>😍 ᴠɪᴅᴇᴏ ᴄʜᴀᴛ sᴛᴀʀᴛᴇᴅ 🥳</b>")
        asyncio.create_task(auto_delete(sent_msg))
        await set_loop(msg.chat.id, 0)
    except Exception:
        pass


@app.on_message(filters.command(["vcstart", "startvc"], ["/", "!"]))
@adminsOnly("can_manage_video_chats")
async def start_group_call(c: Client, m: Message):
    chat_id = m.chat.id
    assistant, ass_id = await _get_assistant_info(chat_id)
    if assistant is None:
        sent_msg = await m.reply("<b>❌ Assistant not found!</b>")
        asyncio.create_task(auto_delete(sent_msg))
        return

    msg = await m.reply("<b>⏳ Starting the Voice Chat…</b>")

    async def _create_call():
        peer = await assistant.resolve_peer(chat_id)
        if isinstance(peer, InputPeerChannel):
            call_peer = InputPeerChannel(channel_id=peer.channel_id, access_hash=peer.access_hash)
        elif isinstance(peer, InputPeerChat):
            call_peer = InputPeerChat(chat_id=peer.chat_id)
        else:
            raise ValueError("Unsupported peer type")
        await assistant.invoke(
            CreateGroupCall(peer=call_peer, random_id=assistant.rnd_id() // 9_000_000_000)
        )

    try:
        await _create_call()
        await set_loop(chat_id, 0)
        await msg.edit_text("<b>🎧 Voice Chat Started Successfully ⚡️</b>")
        asyncio.create_task(auto_delete(msg))

    except ChatAdminRequired:
        try:
            await _grant_vc_manage(chat_id, ass_id)
            await _create_call()
            await _revoke_vc_manage(chat_id, ass_id)
            await set_loop(chat_id, 0)
            await msg.edit_text("<b>🎧 Voice Chat Started Successfully ⚡️</b>")
        except Exception as e:
            await msg.edit_text(
                f"<b>❌ Failed to start VC. Give the bot full permissions.</b>\n<code>{e}</code>"
            )
            asyncio.create_task(auto_delete(msg))

    except Exception as e:
        await msg.edit_text(f"<b>❌ Error:</b> <code>{e}</code>")
        asyncio.create_task(auto_delete(msg))


@app.on_message(filters.command(["vcend", "endvc"], ["/", "!"]))
@adminsOnly("can_manage_video_chats")
async def stop_group_call(c: Client, m: Message):
    chat_id = m.chat.id
    assistant, ass_id = await _get_assistant_info(chat_id)
    if assistant is None:
        sent_msg = await m.reply("<b>❌ Assistant not found!</b>")
        asyncio.create_task(auto_delete(sent_msg))
        return

    msg = await m.reply("<b>⏳ Closing the Voice Chat…</b>")

    async def _discard():
        group_call = await get_group_call(assistant, m, err_msg="(already ended?)")
        if not group_call:
            await msg.delete()
            return False
        await assistant.invoke(DiscardGroupCall(call=group_call))
        return True

    try:
        if await _discard():
            await set_loop(chat_id, 0)
            await msg.edit_text("<b>🎧 Voice Chat Closed Successfully ⚡️</b>")
            asyncio.create_task(auto_delete(msg))

    except Exception as e:
        if "GROUPCALL_FORBIDDEN" in str(e):
            try:
                await _grant_vc_manage(chat_id, ass_id)
                if await _discard():
                    await set_loop(chat_id, 0)
                    await msg.edit_text("<b>🎧 Voice Chat Closed Successfully ⚡️</b>")
                await _revoke_vc_manage(chat_id, ass_id)
            except Exception as ex:
                await msg.edit_text(
                    f"<b>❌ Failed to close VC. Give the bot full permissions.</b>\n<code>{ex}</code>"
                )
                asyncio.create_task(auto_delete(msg))
        else:
            await msg.edit_text(f"<b>❌ Error:</b> <code>{e}</code>")
            asyncio.create_task(auto_delete(msg))


# ── Mute / Unmute all participants ─────────────────────────────────────────────

@app.on_message(filters.command(["vcmute", "mutevc"], ["/", "!"]))
@adminsOnly("can_manage_video_chats")
async def mute_vc(c: Client, m: Message):
    chat_id = m.chat.id
    assistant, _ = await _get_assistant_info(chat_id)
    if assistant is None:
        sent_msg = await m.reply("<b>❌ Assistant not found!</b>")
        asyncio.create_task(auto_delete(sent_msg))
        return
    msg = await m.reply("<b>⏳ Muting all participants…</b>")
    try:
        group_call = await get_group_call(assistant, m)
        if not group_call:
            return await msg.delete()
        # Mute everyone (participants muted = True via call settings)
        await assistant.invoke(
            EditGroupCallParticipant(
                call=group_call,
                participant=await assistant.resolve_peer(chat_id),
                muted=True,
            )
        )
        await msg.edit_text("<b>🔇 All participants muted.</b>")
        asyncio.create_task(auto_delete(msg))
    except Exception as e:
        await msg.edit_text(f"<b>❌ Error:</b> <code>{e}</code>")
        asyncio.create_task(auto_delete(msg))


@app.on_message(filters.command(["vcunmute", "unmutevc"], ["/", "!"]))
@adminsOnly("can_manage_video_chats")
async def unmute_vc(c: Client, m: Message):
    chat_id = m.chat.id
    assistant, _ = await _get_assistant_info(chat_id)
    if assistant is None:
        sent_msg = await m.reply("<b>❌ Assistant not found!</b>")
        asyncio.create_task(auto_delete(sent_msg))
        return
    msg = await m.reply("<b>⏳ Unmuting all participants…</b>")
    try:
        group_call = await get_group_call(assistant, m)
        if not group_call:
            return await msg.delete()
        await assistant.invoke(
            EditGroupCallParticipant(
                call=group_call,
                participant=await assistant.resolve_peer(chat_id),
                muted=False,
            )
        )
        await msg.edit_text("<b>🔊 All participants unmuted.</b>")
        asyncio.create_task(auto_delete(msg))
    except Exception as e:
        await msg.edit_text(f"<b>❌ Error:</b> <code>{e}</code>")
        asyncio.create_task(auto_delete(msg))


# ── VC Status ──────────────────────────────────────────────────────────────────

@app.on_message(filters.command(["vcstatus", "vcinfo"], ["/", "!"]))
@adminsOnly("can_manage_video_chats")
async def vc_status(c: Client, m: Message):
    chat_id = m.chat.id
    assistant, _ = await _get_assistant_info(chat_id)
    if assistant is None:
        sent_msg = await m.reply("<b>❌ Assistant not found!</b>")
        asyncio.create_task(auto_delete(sent_msg))
        return
    try:
        group_call = await get_group_call(assistant, m)
        if not group_call:
            return
        sent_msg = await m.reply(
            f"<b>📡 Voice Chat Status</b>\n"
            f"────────────────────\n"
            f"✅ <b>Active:</b> Yes\n"
            f"🆔 <b>Call ID:</b> <code>{group_call.id}</code>\n"
            f"💬 <b>Chat:</b> {m.chat.title}"
        )
        asyncio.create_task(auto_delete(sent_msg))
    except Exception as e:
        sent_msg = await m.reply(f"<b>❌ Error:</b> <code>{e}</code>")
        asyncio.create_task(auto_delete(sent_msg))


__MODULE__ = "ᴠᴄ ᴍᴀɴᴀɢᴇ"
__HELP__ = """
<b>Voice Chat Management:</b>

• /vcstart — Start the voice chat
• /vcend — End the voice chat
• /vcmute — Mute all participants
• /vcunmute — Unmute all participants
• /vcstatus — Get voice chat info

<i>All commands require <b>Manage Video Chats</b> permission.</i>
"""
