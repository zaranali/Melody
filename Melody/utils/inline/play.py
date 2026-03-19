import math
from pyrogram.types import InlineKeyboardButton
from pyrogram.enums import ButtonStyle
from Melody.utils.formatters import time_to_seconds
from Melody import app
from Melody.misc import db

"""
Inline keyboard markups for music playback and stream control.
Provides various button layouts for searching, playing, and managing streams.
"""

def track_markup(_, videoid, user_id, channel, fplay):
    """Buttons for selecting audio or video when a single track is searched."""
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],  # Audio
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],  # Video
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            )
        ],
    ]
    return buttons

def stream_markup_timer(_, chat_id, played, dur, is_playing=True):
    """Buttons for an active stream with a progress bar and playback controls."""
    # Calculate progress bar
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100 if duration_sec > 0 else 0
    umm = math.floor(percentage)
    filled = min(10, math.floor(umm / 10))
    bar = "▰" * filled + "▱" * (10 - filled)

    # Show queue button only if there are items in the queue
    queue_len = len(db.get(chat_id, []))
    q_btn = []
    if queue_len > 1:
        videoid = db.get(chat_id)[0]['vidid']
        q_btn = [InlineKeyboardButton(text="📋", callback_data=f"GetQueued g|{videoid}", style=ButtonStyle.PRIMARY)]

    buttons = [
        [
            InlineKeyboardButton(
                text=f"{played} {bar} {dur}",
                url=f"https://t.me/{app.username}?startgroup=true"
            )
        ],
        [
            InlineKeyboardButton(text="❚❚" if is_playing else "▶︎", callback_data=f"ADMIN Toggle|{chat_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="⏭", callback_data=f"ADMIN Skip|{chat_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="⏹", callback_data=f"ADMIN Stop|{chat_id}", style=ButtonStyle.DANGER),
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=ButtonStyle.DANGER),
        ],
    ]
    return buttons


def stream_markup(_, chat_id, is_playing=True):
    """Buttons for an active stream without a timer bar (used for live streams or simple view)."""
    queue_len = len(db.get(chat_id, []))
    q_btn = []
    if queue_len > 1:
        videoid = db.get(chat_id)[0]['vidid']
        q_btn = [InlineKeyboardButton(text="📋", callback_data=f"GetQueued g|{videoid}", style=ButtonStyle.PRIMARY)]

    buttons = [
        [
            InlineKeyboardButton(text="❚❚" if is_playing else "▶︎", callback_data=f"ADMIN Toggle|{chat_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="⏭", callback_data=f"ADMIN Skip|{chat_id}", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(text="⏹", callback_data=f"ADMIN Stop|{chat_id}", style=ButtonStyle.DANGER),
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close", style=ButtonStyle.DANGER),
        ],
    ]
    return buttons


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    """Buttons for selecting audio or video when a playlist is searched."""
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MelodyPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MelodyPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons

def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    """Buttons for confirming playback of a live stream."""
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],  # Live Stream
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons

def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    """Navigation buttons for search result sliders."""
    query = f"{query[:20]}"
    buttons = [
        [
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}",
            ),
            InlineKeyboardButton(
                text="▶️",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
        ],
    ]
    return buttons
