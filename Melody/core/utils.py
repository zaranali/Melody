# ── Small-caps translator (fast) ───────────────────────────────────────────────
_SC_SRC = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_SC_DST = "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘǫʀsᴛᴜᴠᴡxʏᴢ"
_SC_TABLE = str.maketrans(_SC_SRC, _SC_DST)

def to_small_caps(text: str) -> str:
    """Convert text to small caps for a stylish look."""
    return text.translate(_SC_TABLE)
