import asyncio
from typing import Union

from Melody.misc import db
from Melody.utils.formatters import check_duration, seconds_to_min
from config import autoclean, time_to_seconds

"""
QUEUE MANAGEMENT UTILS
This module handles the in-memory queue for music playback in different chats.
It provides functions to add tracks to the queue with support for force-play.
"""

async def put_queue(
    chat_id,
    original_chat_id,
    file,
    title,
    duration,
    user,
    vidid,
    user_id,
    stream,
    forceplay: Union[bool, str] = None,
):
    """
    Standard queue insertion logic.
    - formats the title
    - calculates duration in seconds (minus buffer)
    - manages DB insertion (prepend for forceplay, append otherwise)
    """
    title = title.title()
    try:
        # Subtracting 3 seconds to avoid edge-case cutoffs at the end of streams
        duration_in_seconds = time_to_seconds(duration) - 3
    except:
        duration_in_seconds = 0
        
    put = {
        "title": title,
        "dur": duration,
        "streamtype": stream,
        "by": user,
        "user_id": user_id,
        "chat_id": original_chat_id,
        "file": file,
        "vidid": vidid,
        "seconds": duration_in_seconds,
        "played": 0,
    }
    
    if forceplay:
        check = db.get(chat_id)
        if check:
            # Insert at the top of the queue for immediate next playback
            check.insert(0, put)
        else:
            db[chat_id] = []
            db[chat_id].append(put)
    else:
        # Standard append to the end of the queue
        db[chat_id].append(put)
        
    # Track file for automatic cleanup after play
    autoclean.append(file)

async def put_queue_index(
    chat_id,
    original_chat_id,
    file,
    title,
    duration,
    user,
    vidid,
    stream,
    forceplay: Union[bool, str] = None,
):
    """
    Index-based queue insertion, typically used for external URL streams.
    Includes special handling for specific IP-based stream sources.
    """
    # Special check for external stream sources that require duration extraction
    if "20.212.146.162" in vidid:
        try:
            dur = await asyncio.get_event_loop().run_in_executor(
                None, check_duration, vidid
            )
            duration = seconds_to_min(dur)
        except:
            duration = "ᴜʀʟ sᴛʀᴇᴀᴍ"
            dur = 0
    else:
        dur = 0
        
    put = {
        "title": title,
        "dur": duration,
        "streamtype": stream,
        "by": user,
        "chat_id": original_chat_id,
        "file": file,
        "vidid": vidid,
        "seconds": dur,
        "played": 0,
    }
    
    if forceplay:
        check = db.get(chat_id)
        if check:
            check.insert(0, put)
        else:
            db[chat_id] = []
            db[chat_id].append(put)
    else:
        db[chat_id].append(put)
