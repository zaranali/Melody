import os
from pyrogram import filters
from pyrogram.types import Message
from Melody import app, userbot
from Melody.misc import SUDOERS
from Melody.core.utils import to_small_caps

@app.on_message(filters.command(["groupdata", "scrape"]) & SUDOERS)
async def scrape_group_data(client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text(
            f"<b>{to_small_caps('Usage')}:</b> <code>/groupdata @username</code> or <code>/groupdata -1001234567890</code>"
        )
    
    target_chat = message.command[1]
    
    if target_chat.isdigit() or (target_chat.startswith("-") and target_chat[1:].isdigit()):
        target_chat = int(target_chat)
        
    m = await message.reply_text(f"⏳ {to_small_caps('Scraping group data via Assistant... This might take a while depending on the group size.')}")
    
    try:
        ass = userbot.one
        
        try:
            chat = await ass.get_chat(target_chat)
        except Exception as e:
            return await m.edit_text(f"❌ {to_small_caps('Assistant could not access or find the chat')}: `{e}`\n{to_small_caps('Make sure the assistant is in the group.')}")
            
        data = f"Group Name: {chat.title or 'N/A'}\n"
        data += f"Group ID: {chat.id}\n"
        data += f"Username: @{chat.username or 'N/A'}\n"
        data += f"Description: {chat.description or 'N/A'}\n"
        data += f"Members Count: {chat.members_count or 'Unknown'}\n\n"
        data += "-" * 40 + "\n"
        data += "MEMBERS LIST:\n"
        data += "-" * 40 + "\n\n"
        
        count = 0
        async for member in ass.get_chat_members(target_chat):
            count += 1
            user = member.user
            status = member.status.value if hasattr(member.status, 'value') else str(member.status)
            
            data += f"{count}. {user.first_name} {user.last_name or ''}\n"
            data += f"   ID: {user.id}\n"
            data += f"   Username: @{user.username or 'N/A'}\n"
            data += f"   Status: {status}\n"
            data += f"   Is Bot: {user.is_bot}\n"
            data += f"   Is Deleted: {user.is_deleted}\n\n"
            
        data += "-" * 40 + "\n"
        data += f"Total members scraped: {count}\n"
        
        file_name = f"downloads/groupdata_{chat.id}.txt"
        
        os.makedirs("downloads", exist_ok=True)
        
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(data)
            
        await m.edit_text(f"✅ {to_small_caps('Scraping complete! Uploading file...')}")
        
        await message.reply_document(
            document=file_name,
            caption=f"**{to_small_caps('Group Data for')} {chat.title}**\n{to_small_caps('Scraped by Assistant.')}",
            quote=True
        )
        
        await m.delete()
        
        if os.path.exists(file_name):
            os.remove(file_name)
            
    except Exception as e:
        await m.edit_text(f"❌ {to_small_caps('An error occurred during scraping')}: `{e}`")
        if 'file_name' in locals() and os.path.exists(file_name):
            os.remove(file_name)
