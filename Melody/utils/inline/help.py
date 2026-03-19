"""
[Melody Music Bot]
Rebranded and Optimized.
All rights reserved.
"""

from typing import Union
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ButtonStyle
from Melody import app

def help_pannel_page1(_, START: Union[bool, int] = None):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=_["H_B_1"], callback_data="help_callback hb1", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_2"], callback_data="help_callback hb2", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_3"], callback_data="help_callback hb3", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text=_["H_B_4"], callback_data="help_callback hb4", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_5"], callback_data="help_callback hb5", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_6"], callback_data="help_callback hb6", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text=_["H_B_7"], callback_data="help_callback hb7", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_8"], callback_data="help_callback hb8", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_9"], callback_data="help_callback hb9", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text=_["H_B_10"], callback_data="help_callback hb10", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text="◀️", callback_data="help_page_3", style=ButtonStyle.SUCCESS),
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"] if START else _["CLOSE_BUTTON"],
                    callback_data="settingsback_helper" if START else "close",
                    style=ButtonStyle.DANGER
                ),
                InlineKeyboardButton(text="▶️", callback_data="help_page_2", style=ButtonStyle.SUCCESS),
            ],
        ]
    )

def help_pannel_page2(_, START: Union[bool, int] = None):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=_["H_B_11"], callback_data="help_callback hb11", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_12"], callback_data="help_callback hb12", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_13"], callback_data="help_callback hb13", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text=_["H_B_14"], callback_data="help_callback hb14", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_15"], callback_data="help_callback hb15", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text=_["H_B_20"], callback_data="help_callback hb20", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text="◀️", callback_data="help_page_1", style=ButtonStyle.SUCCESS),
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"] if START else _["CLOSE_BUTTON"],
                    callback_data="settingsback_helper" if START else "close",
                    style=ButtonStyle.DANGER
                ),
                InlineKeyboardButton(text="▶️", callback_data="help_page_3", style=ButtonStyle.SUCCESS),
            ],
        ]
    )

def help_pannel_page3(_, START: Union[bool, int] = None):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=_["H_B_21"], callback_data="help_callback hb21", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_23"], callback_data="help_callback hb23", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_24"], callback_data="help_callback hb24", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text=_["H_B_29"], callback_data="help_callback hb29", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton(text=_["H_B_39"], callback_data="help_callback hb39", style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton(text="◀️", callback_data="help_page_2", style=ButtonStyle.SUCCESS),
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"] if START else _["CLOSE_BUTTON"],
                    callback_data="settingsback_helper" if START else "close",
                    style=ButtonStyle.DANGER
                ),
                InlineKeyboardButton(text="▶️", callback_data="help_page_1", style=ButtonStyle.SUCCESS),
            ],
        ]
    )

def help_back_markup(_, page: int = 1):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=_["BACK_BUTTON"],
                    callback_data=f"help_page_{page}",
                    style=ButtonStyle.DANGER
                )
            ]
        ]
    )

def private_help_panel(_):
    return [
        [
            InlineKeyboardButton(
                text=_["S_B_4"],
                url=f"https://t.me/{app.username}?start=help",
                style=ButtonStyle.SUCCESS
            ),
        ]
    ]
