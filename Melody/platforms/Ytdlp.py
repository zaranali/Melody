import asyncio
import os
from typing import Union
from os import path
import yt_dlp

from Melody.utils.formatters import seconds_to_min
from Melody import LOGGER
import config

class YtDlpAPI:
    def __init__(self):
        self.opts = {
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "format": "best",
            "retries": 5,
            "nooverwrites": False,
            "continuedl": True,
            "no_warnings": True,
            "quiet": True,
            "no_cache_dir": True,
            "nocheckcertificate": True,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "http_headers": {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://www.google.com/",
            },
            "cookiefile": "cookies.txt" if path.exists("cookies.txt") else None,
        }

    async def valid(self, link: str):
        def _check_valid():
            extractors = yt_dlp.extractor.gen_extractors()
            for e in extractors:
                if e.suitable(link) and e.IE_NAME != 'generic':
                    return True
            return False
            
        try:
            return await asyncio.get_event_loop().run_in_executor(None, _check_valid)
        except Exception as e:
            LOGGER(__name__).error(f"Error in YtDlp.valid: {e}")
        return False

    async def track(self, link: str):
        def _extract():
            with yt_dlp.YoutubeDL(self.opts) as ydl:
                return ydl.extract_info(link, download=False)
                
        try:
            info = await asyncio.get_event_loop().run_in_executor(None, _extract)
            if not info:
                return {"title": "Unknown", "duration_min": None, "thumb": config.YOUTUBE_IMG_URL}, None
                
            duration = info.get("duration", 0)
            duration_min = seconds_to_min(duration) if duration else None
            thumbnail = info.get("thumbnail") or info.get("thumbnails", [{}])[0].get("url") or config.YOUTUBE_IMG_URL
            
            track_details = {
                "title": info.get("title", "Unknown Title"),
                "duration_min": duration_min,
                "duration_sec": duration,
                "thumb": thumbnail.split("?")[0] if thumbnail != config.YOUTUBE_IMG_URL else thumbnail,
                "vidid": info.get("id", "ytdlp"),
                "link": link
            }
            return track_details, info.get("id", "ytdlp")
        except Exception as e:
            LOGGER(__name__).error(f"Error in YtDlp.track: {e}")
            return {"title": "Unknown", "duration_min": None, "thumb": config.YOUTUBE_IMG_URL}, None

    async def download(self, url: str):
        def _download():
            with yt_dlp.YoutubeDL(self.opts) as ydl:
                return ydl.extract_info(url, download=True)
                
        try:
            info = await asyncio.get_event_loop().run_in_executor(None, _download)
            if not info:
                return False, False
            ext = info.get("ext", "mp4")
            xyz = path.join("downloads", f"{info.get('id', 'ytdlp')}.{ext}")
            
            if os.path.exists(xyz) and os.path.getsize(xyz) > 0:
                duration = info.get("duration", 0)
                duration_min = seconds_to_min(duration)
                track_details = {
                    "title": info.get("title", "Unknown Title"),
                    "duration_sec": duration,
                    "duration_min": duration_min,
                    "uploader": info.get("uploader", "Unknown"),
                    "filepath": xyz,
                    "thumb": info.get("thumbnail", config.YOUTUBE_IMG_URL)
                }
                return track_details, xyz
            return False, False
        except Exception as e:
            LOGGER(__name__).error(f"Error in YtDlp.download: {e}")
            return False, False

