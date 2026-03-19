"""
MELODY MUSIC BOT - CORE INITIALIZATION
This package root handles the initialization of directory structures, 
database connections, and the core client instances (Bot & Userbot).
"""

from .core.bot import MelodyBot
from .core.userbot import Userbot
from .misc import dbb

from .logging import LOGGER
import os

def dirr():
    """
    Initializes required directory structures and performs 
    startup cleanup of temporary image artifacts.
    """
    if "cache" not in os.listdir():
        os.mkdir("cache")
    if "downloads" not in os.listdir():
        os.mkdir("downloads")
    
    # Remove stale thumbnails/images from previous sessions
    for file in os.listdir():
        if file.lower().endswith((".jpg", ".jpeg")):
            try:
                os.remove(file)
            except:
                pass
                
    # Flush the cache directory
    for file in os.listdir("cache"):
        try:
            os.remove(os.path.join("cache", file))
        except:
            pass
    print("[INFO]: CLEANED CACHE & DIRECTORIES")

# Run pre-startup initialization
dirr()
dbb()

# Core instances exported to the package top-level
# 'app' is the main Bot client (Pyrogram)
# 'userbot' handles assistant accounts for streaming
app = MelodyBot()
userbot = Userbot()

# Platform modules (YouTube, Spotify, etc.) are imported last 
# to ensure the 'app' instance is available for their initialization.
from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
YtDlp = YtDlpAPI()
