import json
import os

import redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv('REDIS_URL')
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

CACHE_TTL = 300


def get_cache_key(post_id: int) -> str:
    return f'post:{post_id}'


def get_post_from_cache(post_id: int) -> dict | None:
    key = get_cache_key(post_id)
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None


def set_post_to_cache(post: dict):
    key = get_cache_key(post['id'])
    redis_client.setex(key, CACHE_TTL, json.dumps(post, default=str))


def invalidate_cache(post_id: int):
    key = get_cache_key(post_id)
    redis_client.delete(key)
