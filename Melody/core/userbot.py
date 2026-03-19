from pyrogram import Client
import config
from ..logging import LOGGER
from .utils import to_small_caps

# Global lists to track online assistants and their unique Telegram IDs
assistants = []
assistantids = []

class Userbot:
    """
    Manages multiple assistant accounts (Userbots) using Pyrogram.
    These assistants are responsible for joining voice chats and streaming media.
    """

    def __init__(self):
        # Initialize up to 5 potential assistant clients using provided session strings
        self.one = Client(
            name="MelodyAss1",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING1),
            no_updates=False,
        )
        self.two = Client(
            name="MelodyAss2",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING2),
            no_updates=False,
        )
        self.three = Client(
            name="MelodyAss3",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING3),
            no_updates=False,
        )
        self.four = Client(
            name="MelodyAss4",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING4),
            no_updates=False,
        )
        self.five = Client(
            name="MelodyAss5",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            session_string=str(config.STRING5),
            no_updates=False,
        )

    async def start(self):
        """Starts all assistant clients that have a valid session string configured."""
        LOGGER(__name__).info("Initializing Assistants...")

        # Map of session strings to their respective clients and index
        clients = [
            (config.STRING1, self.one, 1),
            (config.STRING2, self.two, 2),
            (config.STRING3, self.three, 3),
            (config.STRING4, self.four, 4),
            (config.STRING5, self.five, 5),
        ]

        for session, client, number in clients:
            if session:
                try:
                    await client.start()

                    # Cache assistant details
                    client.id = client.me.id
                    client.name = client.me.mention
                    client.username = client.me.username

                    assistants.append(number)
                    assistantids.append(client.id)

                    # Notify log group about assistant status
                    try:
                        await client.send_message(
                            config.LOG_GROUP_ID,
                            f"<b>✨ {to_small_caps(f'Assistant {number} Online')}</b>\n\n"
                            f"<b>{to_small_caps('Name')}:</b> {client.name}\n"
                            f"<b>{to_small_caps('Username')}:</b> @{client.username}\n"
                            f"<b>{to_small_caps('ID')}:</b> <code>{client.id}</code>\n\n"
                            f"<i>{to_small_caps(f'Assistant {number} has successfully authenticated and is ready for playback.')}</i>"
                        )
                    except Exception:
                        LOGGER(__name__).error(
                            f"Assistant {number} failed to message the log group. "
                            "Ensure the assistant is a member and has permission to send messages."
                        )
                    
                    LOGGER(__name__).info(f"Assistant {number} started successfully as {client.name}")
                except Exception as e:
                    LOGGER(__name__).error(f"Failed to start Assistant {number}: {e}")

    async def stop(self):
        """Gracefully stops all assistant clients."""
        LOGGER(__name__).info("Stopping Assistants...")
        clients = [self.one, self.two, self.three, self.four, self.five]
        for client in clients:
            try:
                await client.stop()
            except Exception:
                pass
