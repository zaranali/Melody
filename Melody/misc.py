import time
from pyrogram import filters

import config
from Melody.core.mongo import mongodb

from .logging import LOGGER

SUDOERS = filters.user()

_boot_ = time.time()

XCB = [
    "/",
    "@",
    ".",
    "com",
    ":",
    "https",
]

def dbb():
    global db
    db = {}
    LOGGER(__name__).info(f"Local Database Initialized.")

async def sudo():
    global SUDOERS
    SUDOERS.add(config.OWNER_ID)
    SUDOERS.add(config.DEV_ID)
    sudoersdb = mongodb.sudoers
    sudoers = await sudoersdb.find_one({"sudo": "sudo"})
    sudoers = [] if not sudoers else sudoers["sudoers"]
    if config.OWNER_ID not in sudoers:
        sudoers.append(config.OWNER_ID)
    if config.DEV_ID not in sudoers:
        sudoers.append(config.DEV_ID)
        await sudoersdb.update_one(
            {"sudo": "sudo"},
            {"$set": {"sudoers": sudoers}},
            upsert=True,
        )
    if sudoers:
        for user_id in sudoers:
            SUDOERS.add(user_id)
    LOGGER(__name__).info(f"Sudoers Loaded.")
