from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_DB_URI, MONGO_DB_NAME
from ..logging import LOGGER

"""
MongoDB initialization for the Melody Bot.
This module establishes a connection to the database and provides the 'mongodb' object for use in other modules.
"""

LOGGER(__name__).info("Connecting to MongoDB...")

try:
    # Initialize the asynchronous motor client
    _mongo_async_ = AsyncIOMotorClient(MONGO_DB_URI)

    # Select the database from config
    mongodb = _mongo_async_[MONGO_DB_NAME]

    LOGGER(__name__).info(f"Successfully connected to MongoDB database: {MONGO_DB_NAME}")
except Exception as e:
    # Exit if database connection fails as the bot relies on it for persistent storage
    LOGGER(__name__).error(f"Failed to connect to MongoDB: {e}")
    exit(1)
