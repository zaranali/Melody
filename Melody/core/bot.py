import pyrogram
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config
from .utils import to_small_caps
from ..logging import LOGGER

class MelodyBot(Client):
    """
    The MelodyBot class extends the Pyrogram Client to provide specialized
    functionality for the Melody Music Bot, including automatic logging
    and status checks upon startup.
    """

    def __init__(self):
        LOGGER(__name__).info(f"Initializing bot client...")
        super().__init__(
            name="Melody",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            parse_mode=ParseMode.HTML,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        """Starts the bot client and sends a notification to the log group."""
        await super().start()

        # Cache bot information for easy access
        get_me = await self.get_me()
        self.username = get_me.username
        self.id = get_me.id
        self.name = f"{self.me.first_name} {self.me.last_name or ''}".strip()
        self.mention = self.me.mention

        # Create 'Add to Group' button for the log message
        button = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Add Me To Your Group",
                        url=f"https://t.me/{self.username}?startgroup=true",
                    )
                ]
            ]
        )

        # Notify the log group about the bot status
        if config.LOG_GROUP_ID:
            log_text = (
                f"<b>🚀 {to_small_caps('Melody Music System Live')}</b>\n\n"
                f"<b>{to_small_caps('Bot Name')}:</b> {self.name}\n"
                f"<b>{to_small_caps('Username')}:</b> @{self.username}\n"
                f"<b>{to_small_caps('ID')}:</b> <code>{self.id}</code>\n\n"
                f"<i>{to_small_caps('The core orchestration system is now live and synchronized. All services ready.')}</i>"
            )

            try:
                await self.send_photo(
                    config.LOG_GROUP_ID,
                    photo=config.START_IMG_URL,
                    caption=log_text,
                    reply_markup=button,
                )
            except pyrogram.errors.ChatWriteForbidden:
                LOGGER(__name__).error("Bot cannot write to the log group")
                try:
                    await self.send_message(
                        config.LOG_GROUP_ID,
                        text=log_text,
                        reply_markup=button,
                    )
                except Exception as e:
                    LOGGER(__name__).error(f"Failed to send message in log group: {e}")
            except Exception as e:
                LOGGER(__name__).error(f"Error while sending to log group: {e}")

            # Verify if the bot is an administrator in the log group
            try:
                chat_member_info = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
                if chat_member_info.status != ChatMemberStatus.ADMINISTRATOR:
                    LOGGER(__name__).error("Bot must be an administrator in the Log Group.")
            except Exception as e:
                LOGGER(__name__).error(f"Status check failed: {e}")
        else:
            LOGGER(__name__).warning("LOG_GROUP_ID is not configured.")

        LOGGER(__name__).info(f"Music Bot Started as {self.name}")

    async def stop(self):
        """Stops the bot client safely."""
        await super().stop()
