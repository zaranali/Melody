import asyncio
import importlib
from pyrogram import idle
from pyrogram.types import BotCommand
from pytgcalls.exceptions import NoActiveGroupCall
import config
from Melody import LOGGER, app, userbot
from Melody.core.call import MelodyCall
from Melody.misc import sudo
from Melody.plugins import ALL_MODULES
from Melody.utils.database import get_banned_users, get_gbanned
from config import BANNED_USERS, WEB_SERVICE
from Melody.web import start_web_server
from Melody.core.cookies import fetch_cookies

"""
Main entry point for the Melody Music Bot.
Handles initialization of all components, including plugins, assistants, and web servers.
"""

# Define the list of commands for the bot menu
COMMANDS = [
    # ── Core ────────────────────────────────────────────────────────────────────
    BotCommand("start",       "Start the bot"),
    BotCommand("help",        "Get all commands and help menu"),
    BotCommand("ping",        "Check ping and system stats"),
    BotCommand("stats",       "Show bot statistics"),
    # ── Playback ────────────────────────────────────────────────────────────────
    BotCommand("play",        "Play audio in voice chat"),
    BotCommand("vplay",       "Stream video in voice chat"),
    BotCommand("playrtmps",   "Stream live video content"),
    BotCommand("playforce",   "Force play any audio track"),
    BotCommand("vplayforce",  "Force play any video track"),
    BotCommand("pause",       "Pause the current stream"),
    BotCommand("resume",      "Resume the paused stream"),
    BotCommand("skip",        "Skip the current track"),
    BotCommand("end",         "Stop the ongoing stream"),
    BotCommand("stop",        "Stop the current stream"),
    BotCommand("queue",       "Display the track queue"),
    BotCommand("seek",        "Skip to a specific time"),
    BotCommand("seekback",    "Go back to a previous time"),
    BotCommand("speed",       "Change playback speed in group"),
    BotCommand("loop",        "Enable or disable loop mode"),
    BotCommand("shuffle",     "Randomize the track queue order"),
    # ── Channel ─────────────────────────────────────────────────────────────────
    BotCommand("cplay",       "Play audio in a channel"),
    BotCommand("cvplay",      "Play video in a channel"),
    BotCommand("cplayforce",  "Force play audio in channel"),
    BotCommand("cvplayforce", "Force play video in channel"),
    BotCommand("channelplay", "Link a group to a channel"),
    BotCommand("cspeed",      "Adjust playback speed in channel"),
    # ── Management ──────────────────────────────────────────────────────────────
    BotCommand("auth",        "Add a user to authorized list"),
    BotCommand("unauth",      "Remove user from auth list"),
    BotCommand("authusers",   "Show all authorized users"),
    BotCommand("tagall",      "Mention everyone in the group"),
    # ── VC Management ───────────────────────────────────────────────────────────
    BotCommand("vcstart",     "Start the voice chat"),
    BotCommand("vcend",       "End the voice chat"),
    BotCommand("vcmute",      "Mute all VC participants"),
    BotCommand("vcunmute",    "Unmute all VC participants"),
    BotCommand("vcstatus",    "Show voice chat info"),
    BotCommand("vclogger",    "Toggle VC join/leave logging"),
    # ── Tools ───────────────────────────────────────────────────────────────────
    BotCommand("font",        "Convert text to a stylish font"),
    BotCommand("dl",          "Video downloader"),
]
async def setup_bot_commands():
    """Registers the bot commands with Telegram."""
    try:
        await app.set_bot_commands(COMMANDS)
        LOGGER("Melody").info(f"Bot commands registered successfully ({len(COMMANDS)} commands).")
    except Exception as e:
        LOGGER("Melody").error(f"Failed to register bot commands: {e}")

async def init():
    """Initializes and starts all bot services."""
    # Ensure at least one assistant session is provided
    if not any([config.STRING1, config.STRING2, config.STRING3, config.STRING4, config.STRING5]):
        LOGGER(__name__).error("No Assistant session strings defined. Exiting...")
        return

    # Start optional web server for health checks or other web services
    if WEB_SERVICE:
        asyncio.create_task(start_web_server())

    # Initialize sudo users and fetch necessary cookies for stream platforms
    await sudo()
    await fetch_cookies()

    # Load globally banned users from database
    try:
        gbanned_users = await get_gbanned()
        for user_id in gbanned_users:
            BANNED_USERS.add(user_id)

        banned_users = await get_banned_users()
        for user_id in banned_users:
            BANNED_USERS.add(user_id)
    except Exception:
        pass

    # Start the main bot client
    await app.start()

    # Register commands menu
    await setup_bot_commands()

    # Dynamically import and initialize all plugins
    for module in ALL_MODULES:
        importlib.import_module("Melody.plugins" + module)
    LOGGER("Melody.plugins").info("All modules imported successfully.")

    # Start assistant clients and call manager
    await userbot.start()
    await MelodyCall.start()

    # Verify voice chat availability by attempting a test stream in the log group
    try:
        await MelodyCall.stream_call("https://te.legra.ph/file/29f784eb49d230ab62e9e.mp4")
    except NoActiveGroupCall:
        LOGGER("Melody").error(
            "Log group voice chat is not active. Please start a voice chat in your log group/channel."
        )
        exit(1)
    except Exception:
        pass

    # Initialize pytgcalls decorators
    await MelodyCall.decorators()

    LOGGER("Melody").info("Melody Music Bot is now online.")

    # Keep the bot running until interrupted
    await idle()

    # Graceful shutdown
    await app.stop()
    await userbot.stop()
    LOGGER("Melody").info("Melody Music Bot has stopped.")

if __name__ == "__main__":
    # Start the initialization loop
    asyncio.get_event_loop().run_until_complete(init())
