
import os
import aiohttp
import aiofiles
from pathlib import Path

# Cache directory for fonts
FONT_CACHE_DIR = Path("cache/fonts")
FONT_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Local fallbacks
FALLBACK_BOLD = "Melody/assets/font3.ttf"
FALLBACK_REGULAR = "Melody/assets/font2.ttf"

# Premium fonts mapping (Gstatic direct TTF URLs)
PREMIUM_FONTS = {
    "Outfit-Bold": "https://github.com/google/fonts/raw/main/ofl/outfit/static/Outfit-Bold.ttf",
    "Montserrat-Bold": "https://github.com/google/fonts/raw/main/ofl/montserrat/static/Montserrat-Bold.ttf",
    "Poppins-SemiBold": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-SemiBold.ttf",
    "Raleway-Bold": "https://github.com/google/fonts/raw/main/ofl/raleway/static/Raleway-Bold.ttf",
    "Inter-Bold": "https://github.com/google/fonts/raw/main/ofl/inter/static/Inter-Bold.ttf",
    "NotoSans-Bold": "https://github.com/notofonts/noto-cjk/raw/main/Sans/OTF/Japanese/NotoSansCJKjp-Bold.otf",
}

async def get_font_path(font_name: str, fallback_type: str = "bold") -> str:
    """
    Returns the path to a cached premium font, or a fallback if not found/failed.
    """
    if font_name not in PREMIUM_FONTS:
        return FALLBACK_BOLD if fallback_type == "bold" else FALLBACK_REGULAR

    font_url = PREMIUM_FONTS[font_name]
    font_file = FONT_CACHE_DIR / f"{font_name}.ttf"

    # 1. Return cached if exists
    if font_file.exists():
        return str(font_file)

    # 2. Try to download
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(font_url, timeout=10) as resp:
                if resp.status == 200:
                    async with aiofiles.open(font_file, "wb") as f:
                        await f.write(await resp.read())
                    return str(font_file)
    except Exception as e:
        print(f"[Font Downloader] Failed to fetch {font_name}: {e}")

    # 3. Final Fallback
    return FALLBACK_BOLD if fallback_type == "bold" else FALLBACK_REGULAR
