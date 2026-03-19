import asyncio
from datetime import datetime
from pyrogram.enums import ChatType
from pytgcalls.exceptions import NoActiveGroupCall
import logging
import gc

import config
from Melody import app
from Melody.misc import db
from Melody.core.call import MelodyCall, autoend, counter
from Melody.utils.database import get_client, set_loop, is_active_chat, is_autoend, is_autoleave

async def auto_leave():
    while not await asyncio.sleep(43200):
        from Melody.core.userbot import assistants

        ender = await is_autoleave()
        if not ender:
            continue

        for num in assistants:
            client = await get_client(num)
            left = 0

            try:
                async for i in client.get_dialogs():
                    if i.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP, ChatType.CHANNEL]:
                        if i.chat.id != config.LOG_GROUP_ID:

                            if left == 20:
                                continue

                            if not await is_active_chat(i.chat.id):
                                try:
                                    await client.leave_chat(i.chat.id)
                                    left += 1
                                except Exception as e:
                                    logging.error(f"Error leaving chat {i.chat.id}: {e}")
                                    continue
            except Exception as e:
                logging.error(f"Error processing dialogs: {e}")

asyncio.create_task(auto_leave())

async def auto_end():
    global autoend, counter

    while True:
        await asyncio.sleep(60)

        try:
            ender = await is_autoend()
            if not ender:
                continue

            chatss = autoend
            keys_to_remove = []
            nocall = False

            for chat_id in chatss:
                try:
                    users = len(await MelodyCall.call_listeners(chat_id))
                except NoActiveGroupCall:
                    users = 1
                    nocall = True
                except Exception:
                    users = 100

                timer = autoend.get(chat_id)

                if users == 1:
                    res = await set_loop(chat_id, 0)
                    keys_to_remove.append(chat_id)

                    try:
                        await db[chat_id][0]["mystic"].delete()
                    except Exception:
                        pass

                    try:
                        await MelodyCall.stop_stream(chat_id)
                    except Exception:
                        pass

                    try:
                        if not nocall:
                            await app.send_message(
                                chat_id,
                                "» ʙᴏᴛ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʟᴇғᴛ ᴠɪᴅᴇᴏᴄʜᴀᴛ ʙᴇᴄᴀᴜsᴇ ɴᴏ ᴏɴᴇ ᴡᴀs ʟɪsᴛᴇɴɪɴɢ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ."
                            )
                    except Exception:
                        pass

            for chat_id in keys_to_remove:
                del autoend[chat_id]

            # Force garbage collection to free RAM
            gc.collect()

        except Exception as e:
            logging.info(e)

asyncio.create_task(auto_end())
