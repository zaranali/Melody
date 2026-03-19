import asyncio
import os
import time
from typing import Union

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Voice

import config
from .. import app
from Melody.utils.formatters import (
    check_duration,
    convert_bytes,
    get_readable_time,
    seconds_to_min,
)


class TeleAPI:
    def __init__(self):
        self.chars_limit = 4096
        self.sleep = 5
        self.download_timeout = 1800  # 30 minutes

    async def send_split_text(self, message, string):
        """Sends long text in chunks, capped at 3 messages."""
        n = self.chars_limit
        out = [(string[i : i + n]) for i in range(0, len(string), n)]
        for i, x in enumerate(out[:3]):
            await message.reply_text(x, disable_web_page_preview=True)
        return True

    async def get_link(self, message):
        return message.link

    async def get_filename(self, file, audio: Union[bool, str] = None):
        try:
            file_name = getattr(file, "file_name", None)
            if file_name is None:
                file_name = "ᴛᴇʟᴇɢʀᴀᴍ ᴀᴜᴅɪᴏ" if audio else "ᴛᴇʟᴇɢʀᴀᴍ ᴠɪᴅᴇᴏ"
        except Exception:
            file_name = "ᴛᴇʟᴇɢʀᴀᴍ ᴀᴜᴅɪᴏ" if audio else "ᴛᴇʟᴇɢʀᴀᴍ ᴠɪᴅᴇᴏ"
        return file_name

    async def get_duration(self, filex, file_path: str = None):
        """Get duration from media, with fallback to file probing."""
        try:
            dur = getattr(filex, "duration", None)
            if dur is not None:
                return seconds_to_min(dur)
        except Exception:
            pass

        if file_path and os.path.exists(file_path):
            try:
                dur = await asyncio.get_event_loop().run_in_executor(
                    None, check_duration, file_path
                )
                return seconds_to_min(dur)
            except Exception:
                pass
        return "Unknown"

    async def get_filepath(
        self,
        audio: Union[bool, str] = None,
        video: Union[bool, str] = None,
    ):
        file_name = None
        if audio:
            try:
                ext = (
                    audio.file_name.split(".")[-1]
                    if not isinstance(audio, Voice)
                    else "ogg"
                )
                file_name = f"{audio.file_unique_id}.{ext}"
            except Exception:
                file_name = f"{audio.file_unique_id}.ogg"
        elif video:
            try:
                ext = video.file_name.split(".")[-1]
                file_name = f"{video.file_unique_id}.{ext}"
            except Exception:
                file_name = f"{video.file_unique_id}.mp4"

        if file_name:
            return os.path.join(os.path.realpath("downloads"), file_name)
        return None

    async def download(self, _, message, mystic, fname):
        if os.path.exists(fname):
            return True

        checkpoints = {5, 10, 20, 40, 66, 80, 99}
        sent_checkpoints = set()
        start_time = time.time()

        async def progress(current, total):
            if current == total:
                return

            elapsed = time.time() - start_time
            if elapsed < 0.5:  # Guard against ZeroDivisionError
                return

            percentage = int(current * 100 / total)
            speed = current / elapsed
            eta = get_readable_time(int((total - current) / speed)) if speed > 0 else "..."
            if not eta:
                eta = "0 sᴇᴄᴏɴᴅs"

            total_size = convert_bytes(total)
            completed_size = convert_bytes(current)
            speed_str = convert_bytes(speed)

            for cp in sorted(checkpoints):
                if percentage >= cp and cp not in sent_checkpoints:
                    sent_checkpoints.add(cp)
                    upl = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="ᴄᴀɴᴄᴇʟ",
                                    callback_data="stop_downloading",
                                ),
                            ]
                        ]
                    )
                    try:
                        await mystic.edit_text(
                            text=_["tg_1"].format(
                                app.mention,
                                total_size,
                                completed_size,
                                f"{percentage}%",
                                speed_str,
                                eta,
                            ),
                            reply_markup=upl,
                        )
                    except Exception:
                        pass
                    break

        async def down_load():
            try:
                await app.download_media(
                    message.reply_to_message,
                    file_name=fname,
                    progress=progress,
                )
                elapsed = get_readable_time(int(time.time() - start_time))
                await mystic.edit_text(_["tg_2"].format(elapsed or "0 sᴇᴄᴏɴᴅs"))
            except Exception:
                await mystic.edit_text(_["tg_3"])

        task = asyncio.create_task(down_load())
        config.lyrical[mystic.id] = task

        try:
            await asyncio.wait_for(task, timeout=self.download_timeout)
        except asyncio.TimeoutError:
            task.cancel()
            await mystic.edit_text(_["tg_3"])
        except Exception:
            pass

        verify = config.lyrical.get(mystic.id)
        if not verify:
            return False
        config.lyrical.pop(mystic.id, None)
        return True
