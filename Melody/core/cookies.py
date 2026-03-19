import os
import aiohttp
import config
from Melody import LOGGER

async def fetch_cookies():
    if not config.COOKIES_URL:
        return
    
    LOGGER(__name__).info("Fetching cookies from URL...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(config.COOKIES_URL, timeout=10) as response:
                if response.status == 200:
                    data = await response.text()
                    with open("cookies.txt", "w") as f:
                        f.write(data)
                    LOGGER(__name__).info("Cookies have been fetched and saved successfully as cookies.txt")
                else:
                    LOGGER(__name__).error(f"Failed to fetch cookies: Status {response.status}")
    except Exception as e:
        LOGGER(__name__).error(f"Error while fetching cookies: {e}")
