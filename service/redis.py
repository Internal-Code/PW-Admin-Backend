"""Redis client.

A single lazily-created `redis.asyncio.Redis` connection pool, configured from
`REDIS_URL`. Call `get_redis()` to obtain it and `close_redis()` on shutdown.
"""

from redis.asyncio import Redis, from_url

from config.setting import get_settings

_client: Redis | None = None


def get_redis() -> Redis:
    global _client
    if _client is None:
        _client = from_url(
            get_settings().REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _client


async def close_redis() -> None:
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
