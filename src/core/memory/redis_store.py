import redis
from src.core.config import init_settings

settings = init_settings()

redis_client = redis.Redis.from_url(
    settings.redis_url,
    decode_responses=True
)
