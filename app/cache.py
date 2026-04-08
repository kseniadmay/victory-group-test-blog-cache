import json
from redis.asyncio import Redis
from dotenv import load_dotenv
import os

load_dotenv()

REDIS_URL = os.getenv('REDIS_URL')
redis_client: Redis = Redis.from_url(REDIS_URL, decode_responses=True)

CACHE_TTL = 300


def get_cache_key(post_id: int) -> str:
    return f'post:{post_id}'


async def get_post_from_cache(post_id: int) -> dict | None:
    key = get_cache_key(post_id)
    data = await redis_client.get(key)
    if data:
        return json.loads(data)
    return None


async def set_post_to_cache(post: dict):
    key = get_cache_key(post['id'])
    await redis_client.setex(key, CACHE_TTL, json.dumps(post))


async def invalidate_cache(post_id: int):
    key = get_cache_key(post_id)
    await redis_client.delete(key)
