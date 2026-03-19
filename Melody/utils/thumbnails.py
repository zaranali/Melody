import aiohttp
import aiofiles
import os
import gc
from pathlib import Path
from py_yt import VideosSearch
from PIL import Image, ImageDraw, ImageFont

CACHE_DIR = Path("cache")
CACHE_DIR.mkdir(exist_ok=True)

async def get_font_path(font_name, fallback_type="regular"):
    # Attempting to load predefined app fonts, if not found fallback to default
    try:
        from Melody.utils.fonts import get_font_path as app_font
        return await app_font(font_name, fallback_type)
    except:
        pass
    return None

def truncate_text(text, font, max_width, draw):
    if draw.textlength(text, font=font) <= max_width:
        return text
    while draw.textlength(text + "...", font=font) > max_width:
        text = text[:-1]
        if not text: break
    return text + "..." if text else ""

async def gen_thumb(videoid: str):
    """
    Returns a lightweight, fast, Spotify-like thumbnail.
    """
    url = f"https://www.youtube.com/watch?v={videoid}"
    
    try:
        # Fetch data from YouTube
        results = VideosSearch(url, limit=1)
        result = (await results.next())["result"][0]

        title = result.get("title", "Unknown Title")
        duration = result.get("duration", "Unknown")
        views = result.get("viewCount", {}).get("short", "Unknown Views")
        channel = result.get("channel", {}).get("name", "Unknown Channel")
    except Exception as e:
        print(f"[gen_thumb Info Fetch Error] {e}")
        title = "Melody Player"
        duration = "Unknown"
        views = "Unknown"
        channel = "Melody"

    output_path = CACHE_DIR / f"spot_{videoid}.jpg"
    if output_path.exists():
        return str(output_path)

    # Dark grey-blue color: #121212
    img = Image.new("RGB", (1280, 720), "#121212")
    draw = ImageDraw.Draw(img)

    try:
        title_font_path = await get_font_path("Montserrat-Bold", "bold")
        meta_font_path = await get_font_path("Poppins-SemiBold", "regular")
        noto_font_path = await get_font_path("NotoSans-Bold", "bold")
        
        f_title = ImageFont.truetype(title_font_path, 65) if title_font_path else ImageFont.load_default()
        f_artist = ImageFont.truetype(meta_font_path, 40) if meta_font_path else ImageFont.load_default()
        f_small = ImageFont.truetype(meta_font_path, 24) if meta_font_path else ImageFont.load_default()
        f_tiny = ImageFont.truetype(meta_font_path, 18) if meta_font_path else ImageFont.load_default()
        f_fallback_title = ImageFont.truetype(noto_font_path, 65) if noto_font_path else f_title
        f_fallback_artist = ImageFont.truetype(noto_font_path, 40) if noto_font_path else f_artist
    except:
        f_title = f_artist = f_small = f_tiny = f_fallback_title = f_fallback_artist = ImageFont.load_default()
        
    center_x = 1280 // 2

    # --- BRANDING ---
    from Melody import app
    brand_text = f"Powered by @{app.username}"
    draw.text((40, 40), brand_text, font=f_small, fill="#B3B3B3")

    # --- TOP: "NOW PLAYING" ---
    now_playing = "N O W   P L A Y I N G"
    np_w = draw.textlength(now_playing, font=f_small)
    draw.text((center_x - np_w // 2, 80), now_playing, font=f_small, fill="#1DB954")
    
    # Text drawing helper with fallback
    def draw_text_with_fallback(xy, text, primary_font, fallback_font, fill, draw_obj):
        try:
            draw_obj.text(xy, text, font=primary_font, fill=fill)
        except UnicodeEncodeError:
            draw_obj.text(xy, text, font=fallback_font, fill=fill)
        except Exception:
            draw_obj.text(xy, text, font=fallback_font, fill=fill)

    # --- MIDDLE: Title and Artist ---
    # Title
    title_text = truncate_text(title.strip(), f_fallback_title, 1100, draw)
    title_w = draw.textlength(title_text, font=f_fallback_title)
    draw_text_with_fallback((center_x - title_w // 2, 180), title_text, f_title, f_fallback_title, "#FFFFFF", draw)
    
    # Artist / Channel
    artist_text = truncate_text(channel.strip(), f_fallback_artist, 1100, draw)
    artist_w = draw.textlength(artist_text, font=f_fallback_artist)
    draw_text_with_fallback((center_x - artist_w // 2, 280), artist_text, f_artist, f_fallback_artist, "#B3B3B3", draw)
    
    # --- MIDDLE-LOWER: Metadata Pills ---
    def draw_rounded_rect(draw, xy, radius, fill, outline=None, width=1):
        x0, y0, x1, y1 = xy
        draw.rectangle([(x0, y0 + radius), (x1, y1 - radius)], fill=fill, outline=outline, width=width)
        draw.rectangle([(x0 + radius, y0), (x1 - radius, y1)], fill=fill, outline=outline, width=width)
        draw.pieslice([(x0, y0), (x0 + radius * 2, y0 + radius * 2)], 180, 270, fill=fill, outline=outline, width=width)
        draw.pieslice([(x1 - radius * 2, y0), (x1, y0 + radius * 2)], 270, 360, fill=fill, outline=outline, width=width)
        draw.pieslice([(x0, y1 - radius * 2), (x0 + radius * 2, y1)], 90, 180, fill=fill, outline=outline, width=width)
        draw.pieslice([(x1 - radius * 2, y1 - radius * 2), (x1, y1)], 0, 90, fill=fill, outline=outline, width=width)

    pill_y = 400
    pill_h = 50
    gap = 25
    
    pills = [
        f"⏱ {duration}",
        f"▶ {views} Views",
        "🎵 High Quality Audio"
    ]
    
    total_w = 0
    pill_widths = []
    for p in pills:
        pw = draw.textlength(p, font=f_small) + 60
        pill_widths.append(pw)
        total_w += pw
    total_w += gap * (len(pills) - 1)
    
    start_x = center_x - (total_w / 2)
    
    for i, p in enumerate(pills):
        pw = pill_widths[i]
        draw_rounded_rect(draw, [start_x, pill_y, start_x + pw, pill_y + pill_h], 25, fill="#282828")
        tw = draw.textlength(p, font=f_small)
        draw.text((start_x + (pw - tw)/2, pill_y + 10), p, font=f_small, fill="#FFFFFF")
        start_x += pw + gap
        
    # --- BOTTOM: Playback Controls ---
    ctrl_y = 570
    
    # Play Button (Green Circle)
    cr_large = 45
    draw.ellipse([(center_x - cr_large, ctrl_y - cr_large), 
                  (center_x + cr_large, ctrl_y + cr_large)], fill="#1DB954")
    
    # Play Icon (Triangle)
    tri_w = 30
    tri_h = 35
    offset_x = 5
    draw.polygon([(center_x - tri_w//2 + offset_x, ctrl_y - tri_h//2), 
                  (center_x - tri_w//2 + offset_x, ctrl_y + tri_h//2), 
                  (center_x + tri_w//2 + offset_x, ctrl_y)], fill="black")
                  
    # Previous Button
    prev_x = center_x - 120
    p_tri_w, p_tri_h = 20, 24
    draw.polygon([(prev_x + p_tri_w//2, ctrl_y - p_tri_h//2), 
                  (prev_x + p_tri_w//2, ctrl_y + p_tri_h//2), 
                  (prev_x - p_tri_w//2, ctrl_y)], fill="#FFFFFF")
    draw.rectangle([(prev_x - p_tri_w//2 - 6, ctrl_y - p_tri_h//2), 
                    (prev_x - p_tri_w//2, ctrl_y + p_tri_h//2)], fill="#FFFFFF")
                    
    # Next Button
    next_x = center_x + 120
    draw.polygon([(next_x - p_tri_w//2, ctrl_y - p_tri_h//2), 
                  (next_x - p_tri_w//2, ctrl_y + p_tri_h//2), 
                  (next_x + p_tri_w//2, ctrl_y)], fill="#FFFFFF")
    draw.rectangle([(next_x + p_tri_w//2, ctrl_y - p_tri_h//2), 
                    (next_x + p_tri_w//2 + 6, ctrl_y + p_tri_h//2)], fill="#FFFFFF")
                    
    # Shuffle & Repeat pseudo-icons
    shuf_str = "SHUFFLE"
    rep_str = "REPEAT"
    draw.text((center_x - 240, ctrl_y - 10), shuf_str, font=f_tiny, fill="#B3B3B3")
    draw.text((center_x + 180, ctrl_y - 10), rep_str, font=f_tiny, fill="#B3B3B3")
    
    # Subtle aesthetic line at the bottom
    draw.line([(0, 715), (1280, 715)], fill="#1DB954", width=5)
    
    img.save(output_path, "JPEG", quality=85, optimize=True)
    img.close()
    del img, draw
    gc.collect()

    return str(output_path)

