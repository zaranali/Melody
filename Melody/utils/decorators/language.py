import functools
from Melody import app
from Melody.misc import SUDOERS
from Melody.utils.database import get_lang, is_maintenance
from config import SUPPORT_GROUP
from strings import get_string

def language(mystic):
    @functools.wraps(mystic)
    async def wrapper(_, message, **kwargs):
        if not await is_maintenance():
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    text=f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, ᴠɪsɪᴛ <a href=https://t.me/{SUPPORT_GROUP}>sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a> ғᴏʀ ᴋɴᴏᴡɪɴɢ ᴛʜᴇ ʀᴇᴀsᴏɴ.",
                    disable_web_page_preview=True,
                )
        try:
            await message.delete()
        except:
            pass

        try:
            language = await get_lang(message.chat.id)
            language = get_string(language)
        except:
            language = get_string("en")
        return await mystic(_, message, language)

    return wrapper

def languageCB(mystic):
    @functools.wraps(mystic)
    async def wrapper(_, CallbackQuery, **kwargs):
        if not await is_maintenance():
            if CallbackQuery.from_user.id not in SUDOERS:
                return await CallbackQuery.answer(
                    f"{app.mention} is under maintenance. Visit <a href=https://t.me/{SUPPORT_GROUP}>support chat</a> for info.",
                    show_alert=True,
                )
        try:
            language = await get_lang(CallbackQuery.message.chat.id)
            language = get_string(language)
        except Exception:
            language = get_string("en")
        return await mystic(_, CallbackQuery, language)

    return wrapper

def LanguageStart(mystic):
    @functools.wraps(mystic)
    async def wrapper(_, message, **kwargs):
        try:
            language = await get_lang(message.chat.id)
            language = get_string(language)
        except:
            language = get_string("en")
        return await mystic(_, message, language)

    return wrapper
