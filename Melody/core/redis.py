import sys
from redis import Redis
from config import REDIS_URI

if REDIS_URI:
    try:
        redis_client = Redis.from_url(REDIS_URI, decode_responses=True)
        # Test connection
        redis_client.ping()
        print("[INFO]: Redis cache successfully connected.")
    except Exception as e:
        print(f"[RE-ERR]: Error connecting to Redis: {e}")
        redis_client = None
else:
    redis_client = None
