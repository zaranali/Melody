import asyncio
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls
from pytgcalls.exceptions import NoActiveGroupCall
from pytgcalls.types import Update, ChatUpdate, MediaStream, StreamEnded

import config
from Melody import LOGGER, YouTube, app, userbot
from Melody.misc import db
from Melody.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_assistant,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
    get_audio_bitrate,
    get_video_bitrate,
)
from Melody.utils.exceptions import AssistantErr, CallError
from Melody.utils.formatters import check_duration, seconds_to_min, speed_converter
from Melody.utils.inline.play import stream_markup
from Melody.utils.stream.autoclear import auto_clean
from Melody.utils.thumbnails import gen_thumb
from strings import get_string

# Global dictionaries for managing auto-end functionality
autoend = {}
counter = {}

async def _clear_(chat_id):
    """Clears the queue and active chat status for a specific chat ID."""
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)

class Call(PyTgCalls):
    """
    Handles voice chat streaming using PyTgCalls for multiple assistant accounts.
    Manages playback, seeking, skipping, and speed adjustment.
    """

    def __init__(self):
        # Initialize up to 5 assistant clients for load balancing/multi-client support
        self.one = PyTgCalls(userbot.one, cache_duration=100)
        self.two = PyTgCalls(userbot.two, cache_duration=100)
        self.three = PyTgCalls(userbot.three, cache_duration=100)
        self.four = PyTgCalls(userbot.four, cache_duration=100)
        self.five = PyTgCalls(userbot.five, cache_duration=100)

    async def pause_stream(self, chat_id: int):
        """Pauses the current stream in a chat."""
        assistant = await group_assistant(self, chat_id)
        await assistant.pause(chat_id)

    async def resume_stream(self, chat_id: int):
        """Resumes a paused stream in a chat."""
        assistant = await group_assistant(self, chat_id)
        await assistant.resume(chat_id)

    async def stop_stream(self, chat_id: int):
        """Stops the stream and makes the assistant leave the call."""
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_call(chat_id)
        except Exception as e:
            LOGGER(__name__).error(f"Error stopping stream for {chat_id}: {e}")

    async def stop_stream_force(self, chat_id: int):
        """Forcefully stops the stream across all possible assistant clients."""
        clients = [self.one, self.two, self.three, self.four, self.five]
        sessions = [config.STRING1, config.STRING2, config.STRING3, config.STRING4, config.STRING5]

        for session, client in zip(sessions, clients):
            if session:
                try:
                    await client.leave_call(chat_id)
                except:
                    pass
        try:
            await _clear_(chat_id)
        except Exception as e:
            LOGGER(__name__).error(f"Error clearing chat data for {chat_id}: {e}")

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        """Adjusts the playback speed of the current stream using FFmpeg."""
        assistant = await group_assistant(self, chat_id)
        # Mapping for video PTS adjustment based on speed
        _VS_MAP = {0.5: 2.0, 0.75: 1.35, 1.5: 0.68, 2.0: 0.5}

        if speed != 1.0:
            base = os.path.basename(file_path)
            chatdir = Path(os.getcwd()) / "playback" / str(speed)
            chatdir.mkdir(parents=True, exist_ok=True)
            out = str(chatdir / base)

            if not Path(out).is_file():
                vs = _VS_MAP.get(float(speed))
                if vs is None:
                    raise AssistantErr(f"Unsupported speed value: {speed}")

                # Use FFmpeg to process the file for different playback speeds
                proc = await asyncio.create_subprocess_exec(
                    "ffmpeg",
                    "-i", str(file_path),
                    "-filter:v", f"setpts={vs}*PTS",
                    "-filter:a", f"atempo={speed}",
                    out,
                    stdin=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()
        else:
            out = file_path

        dur = int(await asyncio.to_thread(check_duration, out))
        played, con_seconds = speed_converter(playing[0]["played"], speed)
        duration = seconds_to_min(dur)
        audio_q = await get_audio_bitrate(chat_id)
        video_q = await get_video_bitrate(chat_id)

        # Prepare the media stream with updated parameters
        stream = (
            MediaStream(
                out,
                audio_parameters=audio_q,
                video_parameters=video_q,
                ffmpeg_parameters=f"-ss {played} -to {duration}",
            )
            if playing[0]["streamtype"] == "video"
            else MediaStream(
                out,
                audio_parameters=audio_q,
                ffmpeg_parameters=f"-ss {played} -to {duration}",
            )
        )

        if str(db[chat_id][0]["file"]) == str(file_path):
            await assistant.play(chat_id, stream)
        else:
            raise AssistantErr("Stream data mismatch during speed adjustment.")

        # Update local database with new stream details
        if str(db[chat_id][0]["file"]) == str(file_path):
            if not (playing[0]).get("old_dur"):
                db[chat_id][0]["old_dur"] = db[chat_id][0]["dur"]
                db[chat_id][0]["old_second"] = db[chat_id][0]["seconds"]
            db[chat_id][0]["played"] = con_seconds
            db[chat_id][0]["dur"] = duration
            db[chat_id][0]["seconds"] = dur
            db[chat_id][0]["speed_path"] = out
            db[chat_id][0]["speed"] = speed

    async def force_stop_stream(self, chat_id: int):
        """Forces the stream to stop and clears the queue."""
        assistant = await group_assistant(self, chat_id)
        try:
            check = db.get(chat_id)
            if check:
                check.pop(0)
        except:
            pass
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_call(chat_id)
        except:
            pass

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        """Skips the current stream and plays the provided link."""
        assistant = await group_assistant(self, chat_id)
        audio_q = await get_audio_bitrate(chat_id)
        video_q = await get_video_bitrate(chat_id)

        if video:
            stream = MediaStream(
                link,
                audio_parameters=audio_q,
                video_parameters=video_q,
            )
        else:
            stream = MediaStream(
                link,
                audio_parameters=audio_q,
            )
        await assistant.play(chat_id, stream)

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        """Seeks to a specific timestamp in the current stream."""
        assistant = await group_assistant(self, chat_id)
        audio_q = await get_audio_bitrate(chat_id)
        video_q = await get_video_bitrate(chat_id)

        stream = (
            MediaStream(
                file_path,
                audio_parameters=audio_q,
                video_parameters=video_q,
                ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
            if mode == "video"
            else MediaStream(
                file_path,
                audio_parameters=audio_q,
                ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
        )
        await assistant.play(chat_id, stream)

    async def stream_call(self, link):
        """Temporary stream to the log group to verify voice chat status."""
        assistant = await group_assistant(self, config.LOG_GROUP_ID)
        await assistant.play(config.LOG_GROUP_ID, MediaStream(link))
        await asyncio.sleep(0.2)
        await assistant.leave_call(config.LOG_GROUP_ID)

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        """Joins a voice chat and starts playing the specified media link."""
        if not link:
            raise AssistantErr("Media link not found.")

        assistant = await group_assistant(self, chat_id)
        language = await get_lang(chat_id)
        _ = get_string(language)
        audio_q = await get_audio_bitrate(chat_id)
        video_q = await get_video_bitrate(chat_id)

        if video:
            stream = MediaStream(
                link,
                audio_parameters=audio_q,
                video_parameters=video_q,
            )
        else:
            stream = MediaStream(
                link,
                audio_parameters=audio_q,
            )

        try:
            await assistant.play(chat_id, stream)
        except NoActiveGroupCall:
            raise CallError(_["call_8"])
        except Exception as e:
            if "CHAT_ADMIN_REQUIRED" in str(e):
                user_bot = await get_assistant(chat_id)
                raise CallError(
                    _["call_1"].format(app.mention, user_bot.id, user_bot.name, user_bot.username)
                )
            LOGGER(__name__).error(f"Error joining call: {e}", exc_info=True)
            raise CallError(_["black_9"])

        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)

        if await is_autoend():
            counter[chat_id] = {}
            participants = await assistant.get_participants(chat_id)
            if len(participants) == 1:
                autoend[chat_id] = datetime.now() + timedelta(minutes=1)

    async def change_stream(self, client, chat_id):
        """Handles the transition to the next track in the queue when a stream ends."""
        check = db.get(chat_id)
        popped = None
        loop = await get_loop(chat_id)

        try:
            if loop == 0:
                popped = check.pop(0)
            else:
                await set_loop(chat_id, loop - 1)

            await auto_clean(popped)

            if not check:
                await _clear_(chat_id)
                return await client.leave_call(chat_id)
        except Exception:
            try:
                await _clear_(chat_id)
                return await client.leave_call(chat_id)
            except:
                return

        # Load next track details from the queue
        next_track = check[0]
        queued_file = next_track["file"]
        language = await get_lang(chat_id)
        _ = get_string(language)
        title = next_track["title"].title()
        user = next_track["by"]
        original_chat_id = next_track["chat_id"]
        stream_type = next_track["streamtype"]
        video_id = next_track["vidid"]

        db[chat_id][0]["played"] = 0
        if next_track.get("old_dur"):
            db[chat_id][0]["dur"] = next_track["old_dur"]
            db[chat_id][0]["seconds"] = next_track["old_second"]
            db[chat_id][0]["speed_path"] = None
            db[chat_id][0]["speed"] = 1.0

        is_video = bool(str(stream_type) == "video")
        audio_q = await get_audio_bitrate(chat_id)
        video_q = await get_video_bitrate(chat_id)

        # Handle different types of media links
        if "live_" in queued_file:
            # Handle YouTube Live streams
            n, link = await YouTube.video(video_id, True, is_video=is_video)
            if n == 0:
                return await app.send_message(original_chat_id, text=_["call_6"])

            if is_video:
                stream = MediaStream(link, audio_parameters=audio_q, video_parameters=video_q)
            else:
                stream = MediaStream(link, audio_parameters=audio_q)
            try:
                await client.play(chat_id, stream)
            except:
                return await app.send_message(original_chat_id, text=_["call_6"])

            img = await gen_thumb(video_id)
            button = stream_markup(_, chat_id)
            run = await app.send_photo(
                chat_id=original_chat_id,
                photo=img,
                caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{video_id}", title[:23], next_track["dur"], user),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"

        elif "vid_" in queued_file:
            # Handle downloaded YouTube videos
            mystic = await app.send_message(original_chat_id, _["call_7"])
            try:
                file_path, direct = await YouTube.download(video_id, mystic, videoid=True, video=is_video)
                if not file_path:
                    return await mystic.edit_text(_["call_6"], disable_web_page_preview=True)
            except:
                return await mystic.edit_text(_["call_6"], disable_web_page_preview=True)

            if is_video:
                stream = MediaStream(file_path, audio_parameters=audio_q, video_parameters=video_q)
            else:
                stream = MediaStream(file_path, audio_parameters=audio_q)
            try:
                await client.play(chat_id, stream)
            except:
                return await app.send_message(original_chat_id, text=_["call_6"])

            img = await gen_thumb(video_id)
            button = stream_markup(_, chat_id)
            await mystic.delete()
            run = await app.send_photo(
                chat_id=original_chat_id,
                photo=img,
                caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{video_id}", title[:23], next_track["dur"], user),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"

        elif "index_" in queued_file:
            # Handle Direct Index Links
            if is_video:
                stream = MediaStream(video_id, audio_parameters=audio_q, video_parameters=video_q)
            else:
                stream = MediaStream(video_id, audio_parameters=audio_q)
            try:
                await client.play(chat_id, stream)
            except:
                return await app.send_message(original_chat_id, text=_["call_6"])

            button = stream_markup(_, chat_id)
            run = await app.send_photo(
                chat_id=original_chat_id,
                photo=config.STREAM_IMG_URL,
                caption=_["stream_2"].format(user),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"

        else:
            # Handle other media sources (Telegram, SoundCloud, etc.)
            if is_video:
                stream = MediaStream(queued_file, audio_parameters=audio_q, video_parameters=video_q)
            else:
                stream = MediaStream(queued_file, audio_parameters=audio_q)
            try:
                await client.play(chat_id, stream)
            except:
                return await app.send_message(original_chat_id, text=_["call_6"])

            if video_id == "telegram":
                photo = config.TELEGRAM_AUDIO_URL if str(stream_type) == "audio" else config.TELEGRAM_VIDEO_URL
                source_link = f"https://t.me/{config.SUPPORT_GROUP}"
            elif video_id == "soundcloud":
                photo = config.SOUNCLOUD_IMG_URL
                source_link = f"https://t.me/{config.SUPPORT_GROUP}"
            elif video_id == "ytdlp":
                photo = config.YOUTUBE_IMG_URL
                source_link = f"https://t.me/{config.SUPPORT_GROUP}"
            else:
                photo = await gen_thumb(video_id)
                source_link = f"https://t.me/{app.username}?start=info_{video_id}"

            button = stream_markup(_, chat_id)
            run = await app.send_photo(
                chat_id=original_chat_id,
                photo=photo,
                caption=_["stream_1"].format(source_link, title[:23], next_track["dur"], user),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg" if video_id in ["telegram", "soundcloud", "ytdlp"] else "stream"

    async def ping(self):
        """Returns the average latency of all active assistant clients."""
        pings = []
        clients = [self.one, self.two, self.three, self.four, self.five]
        sessions = [config.STRING1, config.STRING2, config.STRING3, config.STRING4, config.STRING5]

        for session, client in zip(sessions, clients):
            if session:
                pings.append(client.ping)

        return str(round(sum(pings) / len(pings), 3)) if pings else "0.0"

    async def start(self):
        """Starts all configured assistant PyTgCalls clients."""
        LOGGER(__name__).info("Starting Assistant Call Clients...")
        if config.STRING1: await self.one.start()
        if config.STRING2: await self.two.start()
        if config.STRING3: await self.three.start()
        if config.STRING4: await self.four.start()
        if config.STRING5: await self.five.start()

    async def decorators(self):
        """Registers update handlers for stream status changes."""
        clients = [self.one, self.two, self.three, self.four, self.five]

        def register_handler(client):
            @client.on_update()
            async def stream_services_handler(_, update: Update):
                if isinstance(update, StreamEnded):
                    await self.change_stream(client, update.chat_id)
                elif isinstance(update, ChatUpdate) and update.status in [
                    ChatUpdate.Status.KICKED,
                    ChatUpdate.Status.LEFT_GROUP,
                    ChatUpdate.Status.CLOSED_VOICE_CHAT
                ]:
                    await self.stop_stream(update.chat_id)

        for client in clients:
            register_handler(client)

# Global call handler instance
MelodyCall = Call()
