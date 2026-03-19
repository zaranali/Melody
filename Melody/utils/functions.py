from datetime import datetime, timedelta
from re import findall
from re import sub as re_sub

from pyrogram import errors
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message


MARKDOWN = """
ʀᴇᴀᴅ ᴛʜᴇ ʙᴇʟᴏᴡ ᴛᴇxᴛ ᴄᴀʀᴇғᴜʟʟʏ ᴛᴏ ғɪɴᴅ ᴏᴜᴛ ʜᴏᴡ ғᴏʀᴍᴀᴛᴛɪɴɢ ᴡᴏʀᴋs!

<u>sᴜᴘᴘᴏʀᴛᴇᴅ ғɪʟʟɪɴɢs:</u>

{GROUPNAME} - ɢʀᴏᴜᴘ's ɴᴀᴍᴇ
{NAME} - ᴜsᴇʀ ɴᴀᴍᴇ
{ID} - ᴜsᴇʀ ɪᴅ
{FIRSTNAME} - ᴜsᴇʀ ғɪʀsᴛ ɴᴀᴍᴇ
{SURNAME} - ɪғ ᴜsᴇʀ ʜᴀs sᴜʀɴᴀᴍᴇ sᴏ ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ sᴜʀɴᴀᴍᴇ ᴇʟsᴇ ɴᴏᴛʜɪɴɢ
{USERNAME} - ᴜsᴇʀ ᴜsᴇʀɴᴀᴍᴇ

{TIME} - ᴛᴏᴅᴀʏ  ᴛɪᴍᴇ
{DATE} - ᴛᴏᴅᴀʏ ᴅᴀᴛᴇ
{WEEKDAY} - ᴛᴏᴅᴀʏ ᴡᴇᴇᴋᴅᴀʏ

<b><u>NOTE:</u></b> ғɪʟʟɪɴɢs ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ᴡᴇʟᴄᴏᴍᴇ ᴍᴏᴅᴜʟᴇ.

<u>sᴜᴘᴘᴏʀᴛᴇᴅ ғᴏʀᴍᴀᴛᴛɪɴɢ:</u>

<code>**Bold**</code> : ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <b>Bold</b> ᴛᴇxᴛ.
<code>~~strike~~</code>: ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <strike>strike</strike> ᴛᴇxᴛ.
<code>__italic__</code>: ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <i>italic</i> ᴛᴇxᴛ
<code>--underline--</code>: ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <u>underline</u> ᴛᴇxᴛ.
<code>`code words`</code>: ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <code>code</code> ᴛᴇxᴛ.
<code>||spoiler||</code>: ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <spoiler>Spoiler</spoiler> ᴛᴇxᴛ.
<code>[hyperlink](google.com)</code>: ᴛʜɪs ᴡɪʟʟ ᴄʀᴇᴀᴛᴇ ᴀ <a href='https://www.google.com'>hyperlink</a> text
<code>> hello</code>  ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <blockquote>hello</blockquote>
<b>Note:</b> ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ʙᴏᴛʜ ᴍᴀʀᴋᴅᴏᴡɴ & ʜᴛᴍʟ ᴛᴀɢs.

<u>ʙᴜᴛᴛᴏɴ ғᴏʀᴍᴀᴛᴛɪɴɢ:</u>

- > <blockquote>text ~ [button text, button link]</blockquote>

<u>ᴇxᴀᴍᴘʟᴇ:</u>

<b>example</b>
<blockquote><i>button with markdown</i> <code>formatting</code> ~ [button text, https://google.com]</blockquote>
"""
WELCOMEHELP = """
/setwelcome - ʀᴇᴘʟʏ ᴛʜɪs ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴄᴏɴᴛᴀɪɴɪɴɢ ᴄᴏʀʀᴇᴄᴛ
ғᴏʀᴍᴀᴛ ғᴏʀ ᴀ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ, ᴄʜᴇᴄᴋ ᴇɴᴅ ᴏғ ᴛʜɪs ᴍᴇssᴀɢᴇ.

/delwelcome - ᴅᴇʟᴇᴛᴇ ᴛʜᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ.
/getwelcome - ɢᴇᴛ ᴛʜᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ.

<b>SET_WELCOME -></b>

<b>ᴛᴏ sᴇᴛ ᴀ ᴘʜᴏᴛᴏ ᴏʀ ɢɪғ ᴀs ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ. ᴀᴅᴅ ʏᴏᴜʀ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴀs ᴄᴀᴘᴛɪᴏɴ ᴛᴏ ᴛʜᴇ ᴘʜᴏᴛᴏ ᴏʀ ɢɪғ. ᴛʜᴇ ᴄᴀᴘᴛɪᴏɴ ᴍᴜsᴇ ʙᴇ ɪɴ ᴛʜᴇ ғᴏʀᴍᴀᴛ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ.</b>

ғᴏʀ ᴛᴇxᴛ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ ᴊᴜsᴛ sᴇɴᴅ ᴛʜᴇ ᴛᴇxᴛ. ᴛʜᴇɴ ʀᴇᴘʟʏ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ

ᴛʜᴇ ғᴏʀᴍᴀᴛ sʜᴏᴜʟᴅ ʙᴇ sᴏᴍᴇᴛʜɪɴɢ ʟɪᴋᴇ ʙᴇʟᴏᴡ.

{GROUPNAME} - ɢʀᴏᴜᴘ's ɴᴀᴍᴇ
{NAME} - ᴜsᴇʀ ғɪʀsᴛ ɴᴀᴍᴇ + sᴜʀɴᴀᴍᴇ
{ID} - ᴜsᴇʀ ɪᴅ
{FIRSTNAME} - ᴜsᴇʀ ғɪʀsᴛ ɴᴀᴍᴇ
{SURNAME} - ɪғ ᴜsᴇʀ ʜᴀs sᴜʀɴᴀᴍᴇ sᴏ ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ sᴜʀɴᴀᴍᴇ ᴇʟsᴇ ɴᴏᴛʜɪɴɢ
{USERNAME} - ᴜsᴇʀ ᴜsᴇʀɴᴀᴍᴇ

{TIME} - ᴛᴏᴅᴀʏ  ᴛɪᴍᴇ
{DATE} - ᴛᴏᴅᴀʏ ᴅᴀᴛᴇ
{WEEKDAY} - ᴛᴏᴅᴀʏ ᴡᴇᴇᴋᴅᴀʏ

~ #This separater (~) should be there between text and buttons, remove this comment also

button=[Duck, https://duckduckgo.com]

<b>NOTES -></b>

ᴄʜᴇᴄᴋᴏᴜᴛ /markdownhelp ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ ᴀʙᴏᴜᴛ ғᴏʀᴍᴀᴛᴛɪɴɢs ᴀɴᴅ ᴏᴛʜᴇʀ sʏɴᴛᴀx.
"""

def get_urls_from_text(text: str) -> bool:
    regex = r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]
                [.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(
                \([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\
                ()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))""".strip()
    return [x[0] for x in findall(regex, str(text))]

def extract_text_and_keyb(ikb, text: str, row_width: int = 2):
    keyboard = {}
    try:
        text = text.strip()
        if text.startswith("`"):
            text = text[1:]
        if text.endswith("`"):
            text = text[:-1]

        if "~~" in text:
            text = text.replace("~~", "¤¤")
        text, keyb = text.split("~")
        if "¤¤" in text:
            text = text.replace("¤¤", "~~")

        keyb = findall(r"\[.+\,.+\]", keyb)
        for btn_str in keyb:
            btn_str = re_sub(r"[\[\]]", "", btn_str)
            btn_str = btn_str.split(",")
            btn_txt, btn_url = btn_str[0], btn_str[1].strip()

            if not get_urls_from_text(btn_url):
                continue
            keyboard[btn_txt] = btn_url
        keyboard = ikb(keyboard, row_width)
    except Exception:
        return
    return text, keyboard

async def check_format(ikb, raw_text: str):
    keyb = findall(r"\[.+\,.+\]", raw_text)
    if keyb and not "~" in raw_text:
        raw_text = raw_text.replace("button=", "\n~\nbutton=")
        return raw_text
    if "~" in raw_text and keyb:
        if not extract_text_and_keyb(ikb, raw_text):
            return ""
        else:
            return raw_text
    else:
        return raw_text

async def get_data_and_name(replied_message, message):
    text = message.text.markdown if message.text else message.caption.markdown
    name = text.split(None, 1)[1].strip()
    text = name.split(" ", 1)
    if len(text) > 1:
        name = text[0]
        data = text[1].strip()
        if replied_message and (replied_message.sticker or replied_message.video_note):
            data = None
    else:
        if replied_message and (replied_message.sticker or replied_message.video_note):
            data = None
        elif (
            replied_message and not replied_message.text and not replied_message.caption
        ):
            data = None
        else:
            data = (
                replied_message.text.markdown
                if replied_message.text
                else replied_message.caption.markdown
            )
            command = message.command[0]
            match = f"/{command} " + name
            if not message.reply_to_message and message.text:
                if match == data:
                    data = "error"
            elif not message.reply_to_message and not message.text:
                if match == data:
                    data = None
    return data, name

async def extract_userid(message, text: str):
    """
    NOT TO BE USED OUTSIDE THIS FILE
    """

    def is_int(text: str):
        try:
            int(text)
        except ValueError:
            return False
        return True

    text = text.strip()

    if is_int(text):
        return int(text)

    entities = message.entities
    app = message._client
    if len(entities) < 2:
        return (await app.get_users(text)).id
    entity = entities[1]
    if entity.type == MessageEntityType.MENTION:
        return (await app.get_users(text)).id
    if entity.type == MessageEntityType.TEXT_MENTION:
        return entity.user.id
    return None

async def extract_user_and_reason(message, sender_chat=False):
    args = message.text.strip().split()
    text = message.text
    user = None
    reason = None

    try:
        if message.reply_to_message:
            reply = message.reply_to_message
            # if reply to a message and no reason is given
            if not reply.from_user:
                if (
                    reply.sender_chat
                    and reply.sender_chat != message.chat.id
                    and sender_chat
                ):
                    id_ = reply.sender_chat.id
                else:
                    return None, None
            else:
                id_ = reply.from_user.id

            if len(args) < 2:
                reason = None
            else:
                reason = text.split(None, 1)[1]
            return id_, reason

        # if not reply to a message and no reason is given
        if len(args) == 2:
            user = text.split(None, 1)[1]
            return await extract_userid(message, user), None

        # if reason is given
        if len(args) > 2:
            user, reason = text.split(None, 2)[1:]
            return await extract_userid(message, user), reason

        return user, reason

    except errors.UsernameInvalid:
        return "", ""

async def extract_user(message):
    return (await extract_user_and_reason(message))[0]

def get_file_id_from_message(
    message,
    max_file_size=3145728,
    mime_types=["image/png", "image/jpeg"],
):
    file_id = None
    if message.document:
        if int(message.document.file_size) > max_file_size:
            return

        mime_type = message.document.mime_type

        if mime_types and mime_type not in mime_types:
            return
        file_id = message.document.file_id

    if message.sticker:
        if message.sticker.is_animated:
            if not message.sticker.thumbs:
                return
            file_id = message.sticker.thumbs[0].file_id
        else:
            file_id = message.sticker.file_id

    if message.photo:
        file_id = message.photo.file_id

    if message.animation:
        if not message.animation.thumbs:
            return
        file_id = message.animation.thumbs[0].file_id

    if message.video:
        if not message.video.thumbs:
            return
        file_id = message.video.thumbs[0].file_id
    return file_id

async def time_converter(message: Message, time_value: str) -> datetime:
    unit = ["m", "h", "d"]
    check_unit = "".join(list(filter(time_value[-1].lower().endswith, unit)))
    currunt_time = datetime.now()
    time_digit = time_value[:-1]
    if not time_digit.isdigit():
        return await message.reply_text("Incorrect time specified")
    if check_unit == "m":
        temp_time = currunt_time + timedelta(minutes=int(time_digit))
    elif check_unit == "h":
        temp_time = currunt_time + timedelta(hours=int(time_digit))
    elif check_unit == "d":
        temp_time = currunt_time + timedelta(days=int(time_digit))
    else:
        return await message.reply_text("Incorrect time specified.")
    return temp_time
