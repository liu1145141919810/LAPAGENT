import pytest
import pytest_asyncio
import redis.asyncio as redis

@pytest_asyncio.fixture
async def redis_client():
    client = redis.Redis(
        host="127.0.0.1",
        port=6379,
        db=0,
        decode_responses=True,
    )
    try:
        await client.ping()
        yield client
    finally:
        await client.close()
@pytest.mark.asyncio
async def test_redis_set_get(redis_client):
    key = "lapagent:test:pytest"
    try:
        await redis_client.set(
            key,
            "Hello Redis",
            ex=60,
        )
        value = await redis_client.get(key)
        assert value == "Hello Redis"
    finally:
        await redis_client.delete(key)
@pytest.mark.asyncio
async def test_redis_missing_key(redis_client):
    key = "lapagent:test:missing"
    await redis_client.delete(key)
    value = await redis_client.get(key)
    assert value is None
@pytest.mark.asyncio
async def test_redis_delete(redis_client):
    key = "lapagent:test:delete"
    try:
        await redis_client.set(key, "temporary")
        deleted_count = await redis_client.delete(key)
        value = await redis_client.get(key)
        assert deleted_count == 1
        assert value is None
    finally:
        await redis_client.delete(key)
@pytest.mark.asyncio
async def test_redis_ttl(redis_client):
    key = "lapagent:test:ttl"
    try:
        await redis_client.set(
            key,
            "temporary",
            ex=60,
        )
        ttl = await redis_client.ttl(key)
        assert 0 < ttl <= 60
    finally:
        await redis_client.delete(key)