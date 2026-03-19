import asyncio
from collections import deque
from random import randint
from pyrogram import filters
from pyrogram.types import Message

from Melody import app
from Melody.misc import SUDOERS
from Melody.utils.database import get_assistant
from Melody.core.utils import to_small_caps

# ── Emoji Definitions ────────────────────────────────────────────────────────

EMOJIS = {
    "moon": list("🌗🌘🌑🌒🌓🌔🌕🌖"),
    "clock": list("🕙🕘🕗🕖🕕🕔🕓🕒🕑🕐🕛"),
    "thunder": list("☀️🌤️⛅🌥️☁️🌩️🌧️⛈️⚡🌩️🌧️🌦️🌥️⛅🌤️☀️"),
    "earth": list("🌏🌍🌎🌎🌍🌏🌍🌎"),
    "heart": list("❤️🧡💛💚💙💜🖤"),
}

SPECIAL_EMOJIS_DICT = {
    "target": {"emoji": "🎯", "help": "The special target emoji"},
    "dice": {"emoji": "🎲", "help": "The special dice emoji"},
    "bb": {"emoji": "🏀", "help": "The special basketball emoji"},
    "soccer": {"emoji": "⚽️", "help": "The special football emoji"},
}

EMOJI_COMMANDS = list(EMOJIS.keys())
SPECIAL_EMOJI_COMMANDS = list(SPECIAL_EMOJIS_DICT.keys())

# ── Handlers ──────────────────────────────────────────────────────────────────

@app.on_message(filters.command(EMOJI_COMMANDS, ".") & SUDOERS)
async def assistant_emoji_cycle(client, message: Message):
    """
    Cycles through a list of emojis using the assistant for specialized animation.
    """
    command = message.command[0].lower()
    deq = deque(EMOJIS[command])
    
    # Get the assistant for this chat
    assistant = await get_assistant(message.chat.id)
    if not assistant:
        return # Should not happen in most group setups

    # Try to delete original command for a cleaner "userbot" feel if possible
    try:
        await message.delete()
    except:
        pass

    # Assistant sends the initial message
    m = await assistant.send_message(message.chat.id, "".join(deq))
    
    try:
        # Perform the rotation animation
        for _ in range(randint(16, 32)):
            await asyncio.sleep(0.3)
            # Check if deque has data to avoid empty join
            if not deq:
                break
            deq.rotate(1)
            await m.edit("".join(deq))
    except Exception:
        # If it fails (e.g. message deleted), we just stop
        pass

@app.on_message(filters.command(SPECIAL_EMOJI_COMMANDS, ".") & SUDOERS)
async def assistant_special_emojis(client, message: Message):
    """
    Sends special Telegram dice animations via the assistant.
    """
    command = message.command[0].lower()
    data = SPECIAL_EMOJIS_DICT[command]
    
    assistant = await get_assistant(message.chat.id)
    if not assistant:
        return

    try:
        await message.delete()
    except:
        pass
        
    await assistant.send_dice(message.chat.id, data["emoji"])

# ── Module Help ───────────────────────────────────────────────────────────────

__MODULE__ = to_small_caps("Assistant")
__HELP__ = f"""
<b>{to_small_caps("Assistant Fun Commands")}:</b>

• .moon - {to_small_caps("Cycle moon phases")}
• .clock - {to_small_caps("Cycle clock phases")}
• .thunder - {to_small_caps("Cycle weather emojis")}
• .earth - {to_small_caps("Make the world turn")}
• .heart - {to_small_caps("Cycle heart colors")}

<b>{to_small_caps("Special Dice")}:</b>
• .target - {to_small_caps("Throw a dart")}
• .dice - {to_small_caps("Roll a dice")}
• .bb - {to_small_caps("Shoot a basketball")}
• .soccer - {to_small_caps("Kick a football")}

{to_small_caps("Note: These are executed by your assistant account and require SUDO privileges.")}
"""
