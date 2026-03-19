import os
import re
from dotenv import load_dotenv
from pyrogram import filters

# Load environment variables from .env file explicitly
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)

# --- Core Bot Settings ---
# Telegram API credentials from https://my.telegram.org
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", None)

# Bot token from @BotFather
BOT_TOKEN = os.getenv("BOT_TOKEN", None)

# Database URI (MongoDB)
MONGO_DB_URI = os.getenv("MONGO_DB_URI", None)
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "Melody")
REDIS_URI = os.getenv("REDIS_URI", None)

# IDs for various administrative roles
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
_DEV_ID = os.getenv("DEV_ID")
DEV_ID = int(_DEV_ID) if _DEV_ID and _DEV_ID.strip() != "" else OWNER_ID

# Log group ID to receive bot logs
_LOG_GROUP_ID = os.getenv("LOG_GROUP_ID")
LOG_GROUP_ID = int(_LOG_GROUP_ID) if _LOG_GROUP_ID and _LOG_GROUP_ID.strip() not in ("", "0") else OWNER_ID

# --- Support & Social ---
SUPPORT_CHANNEL = os.getenv("SUPPORT_CHANNEL", None)
SUPPORT_GROUP = os.getenv("SUPPORT_GROUP", None)

# --- Web Service Settings ---
WEB_SERVICE = os.getenv("WEB_SERVICE", "False").lower() in ("true", "1", "t")
PORT = int(os.getenv("PORT", "8000"))

# --- Playback Limits ---
DURATION_LIMIT_MIN = int(os.getenv("DURATION_LIMIT", 300))
PLAYLIST_FETCH_LIMIT = int(os.getenv("PLAYLIST_FETCH_LIMIT", 25))

# File size limits (in bytes)
TG_AUDIO_FILESIZE_LIMIT = int(os.getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(os.getenv("TG_VIDEO_FILESIZE_LIMIT", 2145386496))

# --- External API Credentials ---
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", None)
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", None)

# --- Assistant Session Strings ---
STRING1 = os.getenv("STRING_SESSION", None)
STRING2 = os.getenv("STRING_SESSION2", None)
STRING3 = os.getenv("STRING_SESSION3", None)
STRING4 = os.getenv("STRING_SESSION4", None)
STRING5 = os.getenv("STRING_SESSION5", None)

# --- Assistant Settings ---
AUTO_LEAVING_ASSISTANT = os.getenv("AUTO_LEAVING_ASSISTANT", "False").lower() in ("true", "1", "t")

# --- URLs for various services ---
COOKIES_URL = os.getenv("COOKIES_URL", "https://batbin.me/candied")
YT_API_URL = os.getenv("YT_API_URL", "https://shrutibots.site")

# --- Image URLs ---
START_IMG_URL = os.getenv("START_IMG_URL", "https://files.catbox.moe/u05mzo.jpg")
_DEFAULT_IMG = "https://files.catbox.moe/u05mzo.jpg"
PING_IMG_URL = os.getenv("PING_IMG_URL", _DEFAULT_IMG)
PLAYLIST_IMG_URL = os.getenv("PLAYLIST_IMG_URL", _DEFAULT_IMG)
STATS_IMG_URL = os.getenv("STATS_IMG_URL", _DEFAULT_IMG)
TELEGRAM_AUDIO_URL = os.getenv("TELEGRAM_AUDIO_URL", _DEFAULT_IMG)
TELEGRAM_VIDEO_URL = os.getenv("TELEGRAM_VIDEO_URL", _DEFAULT_IMG)
STREAM_IMG_URL = os.getenv("STREAM_IMG_URL", _DEFAULT_IMG)
SOUNCLOUD_IMG_URL = os.getenv("SOUNCLOUD_IMG_URL", _DEFAULT_IMG)
YOUTUBE_IMG_URL = os.getenv("YOUTUBE_IMG_URL", _DEFAULT_IMG)
SPOTIFY_ARTIST_IMG_URL = os.getenv("SPOTIFY_ARTIST_IMG_URL", _DEFAULT_IMG)
SPOTIFY_ALBUM_IMG_URL = os.getenv("SPOTIFY_ALBUM_IMG_URL", _DEFAULT_IMG)
SPOTIFY_PLAYLIST_IMG_URL = os.getenv("SPOTIFY_PLAYLIST_IMG_URL", _DEFAULT_IMG)

# --- Global State Variables ---
BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

# Local cache directory
TEMP_DB_FOLDER = "tempdb"

def time_to_seconds(time):
    """Converts a HH:MM:SS time string to total seconds."""
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))

# Calculated duration limit in seconds
DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

# Username validation regex
_USERNAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{3,31}$")

# Validate support channel and group usernames
if SUPPORT_CHANNEL and not _USERNAME_RE.match(SUPPORT_CHANNEL):
    raise SystemExit(
        f"[ERROR] - SUPPORT_CHANNEL '{SUPPORT_CHANNEL}' is not a valid Telegram username."
    )

if SUPPORT_GROUP and not _USERNAME_RE.match(SUPPORT_GROUP):
    raise SystemExit(
        f"[ERROR] - SUPPORT_GROUP '{SUPPORT_GROUP}' is not a valid Telegram username."
    )
