import random
import string
import traceback
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InputMediaPhoto, Message
from pytgcalls.exceptions import NoActiveGroupCall

import config
from Melody import Apple, Resso, SoundCloud, Spotify, Telegram, YouTube, YtDlp, app
from Melody.core.call import MelodyCall
from Melody import LOGGER
from Melody.utils import seconds_to_min, time_to_seconds
from Melody.utils.channelplay import get_channeplayCB
from Melody.utils.database import is_on_off
from Melody.utils.decorators.language import languageCB
from Melody.utils.decorators.play import PlayWrapper
from Melody.utils.exceptions import MelodyError, AssistantErr, CallError, PlatformError
from Melody.utils.formatters import formats
from Melody.utils.inline import (
    botplaylist_markup,
    livestream_markup,
    playlist_markup,
    slider_markup,
    track_markup,
)
from Melody.utils.logger import play_logs
from Melody.utils.stream.stream import stream
from config import BANNED_USERS, lyrical

async def handle_telegram(_, mystic, user_id, user_name, chat_id, message, audio, video, fplay):
    """
    Handles playback of media files uploaded directly to Telegram (Audio/Video).
    1. Validates file size and duration limits.
    2. Downloads the file to the local 'downloads' directory.
    3. Initiates the playback stream via pytgcalls.
    """
    telegram_media = audio or video
    if audio:
        if audio.file_size > 104857600:
            return await mystic.edit_text(_["play_5"])
        if audio.duration > config.DURATION_LIMIT:
            return await mystic.edit_text(_["play_6"].format(config.DURATION_LIMIT_MIN, app.mention))
    elif video:
        if message.reply_to_message.document:
            try:
                ext = video.file_name.split(".")[-1]
                if ext.lower() not in formats:
                    return await mystic.edit_text(_["play_7"].format(" | ".join(formats)))
            except:
                return await mystic.edit_text(_["play_7"].format(" | ".join(formats)))
        if video.file_size > config.TG_VIDEO_FILESIZE_LIMIT:
            return await mystic.edit_text(_["play_8"])

    file_path = await Telegram.get_filepath(audio=audio, video=video)
    if await Telegram.download(_, message, mystic, file_path):
        message_link = await Telegram.get_link(message)
        file_name = await Telegram.get_filename(telegram_media, audio=bool(audio))
        dur = await Telegram.get_duration(telegram_media, file_path)
        details = {
            "title": file_name,
            "link": message_link,
            "path": file_path,
            "dur": dur,
            "thumb": config.TELEGRAM_VIDEO_URL if video else config.TELEGRAM_AUDIO_URL,
        }
        try:
            await stream(_, mystic, user_id, details, chat_id, user_name, message.chat.id, video=bool(video), streamtype="telegram", forceplay=fplay)
        except MelodyError as e:
            try:
                return await mystic.edit_text(str(e))
            except:
                return await message.reply_text(str(e))
        except Exception as e:
            LOGGER(__name__).error(f"Unexpected error in handle_telegram: {e}", exc_info=True)
            err = _["general_2"].format(type(e).__name__)
            try:
                return await mystic.edit_text(err)
            except:
                return await message.reply_text(err)
        try:
            await mystic.delete()
        except:
            pass
        return True
    return False

@app.on_message(filters.command(["play", "vplay", "cplay", "cvplay", "playforce", "vplayforce", "cplayforce", "cvplayforce"]) & filters.group & ~BANNED_USERS)
@PlayWrapper
async def play_commnd(client, message: Message, _, chat_id, video, channel, playmode, url, fplay):
    """
    Main entry point for all playback commands.
    Logic Flow:
    1. Check if the message is a reply to a TG file.
    2. If a URL is provided, determine the platform (YouTube, Spotify, Apple, etc.).
    3. If it's a text query, search YouTube.
    4. Handle 'Direct' play vs 'Playlist' selection menus.
    """
    mystic = await message.reply_text(_["play_2"].format(channel) if channel else _["play_1"])
    user_id, user_name = message.from_user.id, message.from_user.first_name
    audio_tg = (message.reply_to_message.audio or message.reply_to_message.voice) if message.reply_to_message else None
    video_tg = (message.reply_to_message.video or message.reply_to_message.document) if message.reply_to_message else None

    if audio_tg or video_tg:
        if await handle_telegram(_, mystic, user_id, user_name, chat_id, message, audio_tg, video_tg, fplay):
            return

    if url:
        # Platform detection logic
        if await YouTube.exists(url):
            if "playlist" in url or "list=" in url:
                try:
                    details = await YouTube.playlist(url, config.PLAYLIST_FETCH_LIMIT, user_id)
                except:
                    return await mystic.edit_text(_["play_3"])
                streamtype, plist_type, img, cap = "playlist", "yt", config.PLAYLIST_IMG_URL, _["play_9"]
                plist_id = url.split("list=")[1].split("&")[0] if "list=" in url else url.split("=")[1]
            else:
                try:
                    details, track_id = await YouTube.track(url)
                except:
                    return await mystic.edit_text(_["play_3"])
                streamtype, img = "youtube", details["thumb"]
                cap = _["play_10"].format(details["title"], details["duration_min"])
        elif await Spotify.valid(url):
            if not (config.SPOTIFY_CLIENT_ID and config.SPOTIFY_CLIENT_SECRET):
                return await mystic.edit_text("» sᴘᴏᴛɪғʏ ɪs ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ ʏᴇᴛ.\n\nᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.")
            if "track" in url:
                try: 
                    details, track_id = await Spotify.track(url)
                except: 
                    return await mystic.edit_text(_["play_3"])
                streamtype, img = "youtube", details["thumb"]
                cap = _["play_10"].format(details["title"], details["duration_min"])
            else:
                try:
                    if "playlist" in url:
                        details, plist_id = await Spotify.playlist(url)
                        plist_type, img = "spplay", config.SPOTIFY_PLAYLIST_IMG_URL
                    elif "album" in url:
                        details, plist_id = await Spotify.album(url)
                        plist_type, img = "spalbum", config.SPOTIFY_ALBUM_IMG_URL
                    elif "artist" in url:
                        details, plist_id = await Spotify.artist(url)
                        plist_type, img = "spartist", config.SPOTIFY_ARTIST_IMG_URL
                    else: 
                        return await mystic.edit_text(_["play_15"])
                except: 
                    return await mystic.edit_text(_["play_3"])
                streamtype, cap = "playlist", _["play_11"].format(app.mention, message.from_user.mention)
        elif await Apple.valid(url):
            try:
                if "album" in url:
                    details, track_id = await Apple.track(url)
                    streamtype, img = "youtube", details["thumb"]
                    cap = _["play_10"].format(details["title"], details["duration_min"])
                elif "playlist" in url:
                    details, plist_id = await Apple.playlist(url)
                    streamtype, plist_type, cap, img = "playlist", "apple", _["play_12"].format(app.mention, message.from_user.mention), url
                else: return await mystic.edit_text(_["play_3"])
            except: return await mystic.edit_text(_["play_3"])
        elif await Resso.valid(url):
            try:
                details, track_id = await Resso.track(url)
                streamtype, img = "youtube", details["thumb"]
                cap = _["play_10"].format(details["title"], details["duration_min"])
            except: return await mystic.edit_text(_["play_3"])
        elif await SoundCloud.valid(url):
            try:
                details, track_path = await SoundCloud.download(url)
                if details["duration_sec"] > config.DURATION_LIMIT:
                    return await mystic.edit_text(_["play_6"].format(config.DURATION_LIMIT_MIN, app.mention))
                await stream(_, mystic, user_id, details, chat_id, user_name, message.chat.id, streamtype="soundcloud", forceplay=fplay)
                await mystic.delete()
                return
            except MelodyError as e:
                return await mystic.edit_text(str(e))
            except Exception as e:
                LOGGER(__name__).error(f"SoundCloud error: {e}", exc_info=True)
                return await mystic.edit_text(_["black_9"])
        elif await YtDlp.valid(url):
            try:
                details, track_id = await YtDlp.track(url)
                streamtype, img = "ytdlp", details["thumb"]
                cap = _["play_10"].format(details["title"], details["duration_min"])
            except Exception as e:
                return await mystic.edit_text(f"Error processing generic link: {e}")
        else:
            try: await MelodyCall.stream_call(url)
            except NoActiveGroupCall:
                await mystic.edit_text(_["black_9"])
                return await app.send_message(chat_id=config.LOG_GROUP_ID, text=_["play_17"])
            except Exception as e: 
                LOGGER(__name__).error(f"Index stream error: {traceback.format_exc()}")
                return await mystic.edit_text(_["black_9"])
            await mystic.edit_text(_["str_2"])
            try: await stream(_, mystic, user_id, url, chat_id, user_name, message.chat.id, video=video, streamtype="index", forceplay=fplay)
            except MelodyError as e:
                return await mystic.edit_text(str(e))
            except Exception as e:
                LOGGER(__name__).error(f"Index stream inner error: {traceback.format_exc()}")
                return await mystic.edit_text(_["black_9"])

            return await play_logs(message, streamtype="M3u8 or Index Link")
    else:
        if len(message.command) < 2:
            return await mystic.edit_text(_["play_18"], reply_markup=InlineKeyboardMarkup(botplaylist_markup(_)))
        query = message.text.split(None, 1)[1]
        try: details, track_id = await YouTube.track(query)
        except: return await mystic.edit_text(_["play_3"])
        streamtype, slider = "youtube", True

    if str(playmode) == "Direct":
        if 'plist_type' not in locals():
            if details.get("duration_min"):
                if time_to_seconds(details["duration_min"]) > config.DURATION_LIMIT:
                    return await mystic.edit_text(_["play_6"].format(config.DURATION_LIMIT_MIN, app.mention))
            else:
                buttons = livestream_markup(_, track_id, user_id, "v" if video else "a", "c" if channel else "g", "f" if fplay else "d")
                return await mystic.edit_text(_["play_13"], reply_markup=InlineKeyboardMarkup(buttons))
        try:
            await stream(_, mystic, user_id, details, chat_id, user_name, message.chat.id, video=video, streamtype=streamtype, spotify='spotify' in locals() or 'plist_type' in locals() and plist_type != "yt", forceplay=fplay)
        except MelodyError as e:
            return await mystic.edit_text(str(e))
        except Exception as e:
            LOGGER(__name__).error(f"Direct play stream error: {traceback.format_exc()}")
            return await mystic.edit_text(_["black_9"])
        await mystic.delete()
        return await play_logs(message, streamtype=streamtype)
    else:
        if 'plist_type' in locals():
            ran_hash = "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
            lyrical[ran_hash] = plist_id
            buttons = playlist_markup(_, ran_hash, user_id, plist_type, "c" if channel else "g", "f" if fplay else "d")
            await mystic.delete()
            await message.reply_photo(photo=img, caption=cap, reply_markup=InlineKeyboardMarkup(buttons))
            return await play_logs(message, streamtype=f"Playlist : {plist_type}")
        else:
            if 'slider' in locals():
                buttons = slider_markup(_, track_id, user_id, query, 0, "c" if channel else "g", "f" if fplay else "d")
                await mystic.delete()
                await message.reply_photo(photo=details["thumb"], caption=_["play_10"].format(details["title"].title(), details["duration_min"]), reply_markup=InlineKeyboardMarkup(buttons))
                return await play_logs(message, streamtype=f"Searched on Youtube")
            else:
                buttons = track_markup(_, track_id, user_id, "c" if channel else "g", "f" if fplay else "d")
                await mystic.delete()
                await message.reply_photo(photo=img, caption=cap, reply_markup=InlineKeyboardMarkup(buttons))
                return await play_logs(message, streamtype=f"URL Searched Inline")

@app.on_callback_query(filters.regex("MusicStream") & ~BANNED_USERS)
@languageCB
async def play_music(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    vidid, user_id, mode, cplay, fplay = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        try:
            return await CallbackQuery.answer(_["playcb_1"], show_alert=True)
        except:
            return
    try:
        chat_id, channel = await get_channeplayCB(_, cplay, CallbackQuery)
    except:
        return
    user_name = CallbackQuery.from_user.first_name
    try:
        await CallbackQuery.message.delete()
        await CallbackQuery.answer()
    except:
        pass
    mystic = await CallbackQuery.message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )
    try:
        details, track_id = await YouTube.track(vidid, True)
    except:
        return await mystic.edit_text(_["play_3"])
    if details["duration_min"]:
        duration_sec = time_to_seconds(details["duration_min"])
        if duration_sec > config.DURATION_LIMIT:
            return await mystic.edit_text(
                _["play_6"].format(config.DURATION_LIMIT_MIN, app.mention)
            )
    else:
        buttons = livestream_markup(
            _,
            track_id,
            CallbackQuery.from_user.id,
            mode,
            "c" if cplay == "c" else "g",
            "f" if fplay else "d",
        )
        return await mystic.edit_text(
            _["play_13"],
            reply_markup=InlineKeyboardMarkup(buttons),
        )
    video = True if mode == "v" else None
    ffplay = True if fplay == "f" else None
    try:
        await stream(
            _,
            mystic,
            CallbackQuery.from_user.id,
            details,
            chat_id,
            user_name,
            CallbackQuery.message.chat.id,
            video,
            streamtype="youtube",
            forceplay=ffplay,
        )
    except MelodyError as e:
        return await mystic.edit_text(str(e))
    except Exception as e:
        LOGGER(__name__).error(f"YouTube callback stream error: {e}", exc_info=True)
        return await mystic.edit_text(_["black_9"])
    return await mystic.delete()

@app.on_callback_query(filters.regex("AnonymousAdmin") & ~BANNED_USERS)
async def anonymous_check(client, CallbackQuery):
    try:
        await CallbackQuery.answer(
            "» ʀᴇᴠᴇʀᴛ ʙᴀᴄᴋ ᴛᴏ ᴜsᴇʀ ᴀᴄᴄᴏᴜɴᴛ :\n\nᴏᴘᴇɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ sᴇᴛᴛɪɴɢs.\n-> ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀs\n-> ᴄʟɪᴄᴋ ᴏɴ ʏᴏᴜʀ ɴᴀᴍᴇ\n-> ᴜɴᴄʜᴇᴄᴋ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ ᴘᴇʀᴍɪssɪᴏɴs.",
            show_alert=True,
        )
    except:
        pass

@app.on_callback_query(filters.regex("MelodyPlaylists") & ~BANNED_USERS)
@languageCB
async def play_playlists_command(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    (
        videoid,
        user_id,
        ptype,
        mode,
        cplay,
        fplay,
    ) = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        try:
            return await CallbackQuery.answer(_["playcb_1"], show_alert=True)
        except:
            return
    try:
        chat_id, channel = await get_channeplayCB(_, cplay, CallbackQuery)
    except:
        return
    user_name = CallbackQuery.from_user.first_name
    await CallbackQuery.message.delete()
    try:
        await CallbackQuery.answer()
    except:
        pass
    mystic = await CallbackQuery.message.reply_text(
        _["play_2"].format(channel) if channel else _["play_1"]
    )
    videoid = lyrical.get(videoid)
    video = True if mode == "v" else None
    ffplay = True if fplay == "f" else None
    spotify = True
    if ptype == "yt":
        spotify = False
        try:
            result = await YouTube.playlist(
                videoid,
                config.PLAYLIST_FETCH_LIMIT,
                CallbackQuery.from_user.id,
                True,
            )
        except:
            return await mystic.edit_text(_["play_3"])
    if ptype == "spplay":
        try:
            result, spotify_id = await Spotify.playlist(videoid)
        except:
            return await mystic.edit_text(_["play_3"])
    if ptype == "spalbum":
        try:
            result, spotify_id = await Spotify.album(videoid)
        except:
            return await mystic.edit_text(_["play_3"])
    if ptype == "spartist":
        try:
            result, spotify_id = await Spotify.artist(videoid)
        except:
            return await mystic.edit_text(_["play_3"])
    if ptype == "apple":
        try:
            result, apple_id = await Apple.playlist(videoid, True)
        except:
            return await mystic.edit_text(_["play_3"])
    try:
        await stream(
            _,
            mystic,
            user_id,
            result,
            chat_id,
            user_name,
            CallbackQuery.message.chat.id,
            video,
            streamtype="playlist",
            spotify=spotify,
            forceplay=ffplay,
        )
    except Exception as e:
        print(f"Error: {e}")
        ex_type = type(e).__name__
        err = e if ex_type == "AssistantErr" else _["general_2"].format(ex_type)
        return await mystic.edit_text(err)
    return await mystic.delete()

@app.on_callback_query(filters.regex("slider") & ~BANNED_USERS)
@languageCB
async def slider_queries(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    (
        what,
        rtype,
        query,
        user_id,
        cplay,
        fplay,
    ) = callback_request.split("|")
    if CallbackQuery.from_user.id != int(user_id):
        try:
            return await CallbackQuery.answer(_["playcb_1"], show_alert=True)
        except:
            return
    what = str(what)
    rtype = int(rtype)
    if what == "F":
        if rtype == 9:
            query_type = 0
        else:
            query_type = int(rtype + 1)
        try:
            await CallbackQuery.answer(_["playcb_2"])
        except:
            pass
        title, duration_min, thumbnail, vidid = await YouTube.slider(query, query_type)
        buttons = slider_markup(_, vidid, user_id, query, query_type, cplay, fplay)
        med = InputMediaPhoto(
            media=thumbnail,
            caption=_["play_10"].format(
                title.title(),
                duration_min,
            ),
        )
        return await CallbackQuery.edit_message_media(
            media=med, reply_markup=InlineKeyboardMarkup(buttons)
        )
    if what == "B":
        if rtype == 0:
            query_type = 9
        else:
            query_type = int(rtype - 1)
        try:
            await CallbackQuery.answer(_["playcb_2"])
        except:
            pass
        title, duration_min, thumbnail, vidid = await YouTube.slider(query, query_type)
        buttons = slider_markup(_, vidid, user_id, query, query_type, cplay, fplay)
        med = InputMediaPhoto(
            media=thumbnail,
            caption=_["play_10"].format(
                title.title(),
                duration_min,
            ),
        )
        return await CallbackQuery.edit_message_media(
            media=med, reply_markup=InlineKeyboardMarkup(buttons)
        )
