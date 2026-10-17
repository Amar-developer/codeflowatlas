import hashlib
import logging
import os

from fastapi import HTTPException
from redis.asyncio import Redis
from redis.exceptions import RedisError

redis = Redis.from_url(
    os.environ["REDIS_URL"],
    decode_responses=True,
)
logger = logging.getLogger(__name__)

INCREMENT_WITH_EXPIRY = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return count
"""

REFUND_IF_PRESENT = """
local count = redis.call('GET', KEYS[1])
if not count then return 0 end
if tonumber(count) <= 1 then
    redis.call('DEL', KEYS[1])
else
    redis.call('DECR', KEYS[1])
end
return 1
"""


def _limit_key(action: str, identifier: str) -> str:
    digest = hashlib.sha256(
        identifier.strip().casefold().encode("utf-8")
    ).hexdigest()
    return f"auth-limit:{action}:{digest}"


async def enforce_limit(
    action: str,
    identifier: str,
    limit: int,
    window_seconds: int,
) -> None:
    key = _limit_key(action, identifier)

    try:
        count = int(
            await redis.eval(
                INCREMENT_WITH_EXPIRY,
                1,
                key,
                window_seconds,
            )
        )
    except RedisError as exc:
        raise HTTPException(
            status_code=503,
            detail="Authentication is temporarily unavailable",
        ) from exc

    if count > limit:
        raise HTTPException(
            status_code=429,
            detail="Too many attempts. Try again later.",
            headers={"Retry-After": str(window_seconds)},
        )


async def refund_limit(action: str, identifier: str) -> None:
    """Return a mail-attempt allowance when SMTP failed before delivery."""
    try:
        await redis.eval(REFUND_IF_PRESENT, 1, _limit_key(action, identifier))
    except RedisError:
        logger.exception("Could not refund authentication mail rate limit")
