import os

from ..logging import LOGGER

def dirr():
    for file in os.listdir():
        if file.endswith(".jpg"):
            os.remove(file)
        elif file.endswith(".jpeg"):
            os.remove(file)
        elif file.endswith(".png"):
            os.remove(file)

    for d in ["downloads", "cache", "tempdb"]:
        if not os.path.exists(d):
            os.mkdir(d)

    LOGGER(__name__).info("Directories Updated.")
