from pyrogram.types import InlineKeyboardButton
from pyrogram.enums import ButtonStyle
import config
from Melody import app

def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"], url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.PRIMARY
            ),
            InlineKeyboardButton(text=_["S_B_2"], url=f"https://t.me/{config.SUPPORT_GROUP}"),
        ],
        [
            InlineKeyboardButton(text="ᴀʙᴏᴜᴛ", callback_data="about_page"),
        ],
    ]
    return buttons

def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
                style=ButtonStyle.PRIMARY
            )
        ],
        [
            InlineKeyboardButton(text="ᴀʙᴏᴜᴛ", callback_data="about_page"),
            InlineKeyboardButton(text="ᴏᴡɴᴇʀ", callback_data="owner_page"),
        ],
          [
            InlineKeyboardButton(text="ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs", callback_data="help_page_1", style=ButtonStyle.SUCCESS),
        ],
    ]
    return buttons

def about_panel(_):
    buttons = [
        [
            InlineKeyboardButton(text="ᴄʜᴀɴɴᴇʟ", url=f"https://t.me/{config.SUPPORT_CHANNEL}"),
            InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{config.SUPPORT_GROUP}"),
        ],
        [
            InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="settingsback_helper", style=ButtonStyle.DANGER)
        ]
    ]
    return buttons

def owner_panel(_):
    buttons = [
        [
            InlineKeyboardButton(text=_["S_B_12"], user_id=config.OWNER_ID),
            InlineKeyboardButton(text=_["S_B_5"], user_id=config.DEV_ID),
        ],
        [
            InlineKeyboardButton(text=_["BACK_BUTTON"], callback_data="settingsback_helper", style=ButtonStyle.DANGER),
        ]
    ]
    return buttons
