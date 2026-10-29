import os
import json
import asyncio
from contextlib import asynccontextmanager
import configparser

from fastapi import FastAPI
import redis.asyncio as redis
from redis.exceptions import RedisError

from public.logger import setup_logger
logger = setup_logger(__name__)

_current_dir = os.path.dirname(os.path.abspath(__file__))
_config_path = os.path.join(_current_dir, '..', 'public', 'public_config.ini')
cfg = configparser.ConfigParser()
cfg.read(_config_path)

class RedisManager:
    def __init__(self):
        redis_url = os.getenv("LAPAGENT_REDIS_URL", "redis://127.0.0.1:6379")
        if not redis_url:
            redis_url = cfg.get("Redis", "url", fallback="redis://127.0.0.1:6379")
        with open(os.path.join(_current_dir, '..', 'public', 'public_config.ini'), 'w') as configfile:
            if not cfg.has_section("Redis"):
                cfg.add_section("Redis")
            cfg.set("Redis", "url", redis_url)
            cfg.write(configfile)
            logger.info(f"Redis URL has been set and saved successfully")
    
        self.client = redis.from_url(
            redis_url,
            decode_responses=True,
            socket_connect_timeout=2,
            health_check_interval=30,
        )
        self.available = False
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        # default degraded state: Redis is unavailable
        app.state.redis_available = False
        app.state.redis = None

        # Set the multiple try
        max_attempts = 3
        for attempt in range(max_attempts):
            try:
                await self.client.ping()
                app.state.redis_available = True
                app.state.redis = self.client
                logger.info("Successfully connected to Redis.")
                self.available = True
                break
            except RedisError as e:
                logger.warning(f"Redis ping failed ({attempt}/{max_attempts}): {e}")
                if attempt < max_attempts-1:
                    await asyncio.sleep(1.0)
                else:
                    logger.warning("Redis unavailable, running in degraded mode.")
        try:
            yield
        finally:
            # Use aclose, avoid deprecation warnings from close()
            try:
                await self.client.aclose()
                logger.info("Redis connection closed.")
            except RedisError as e:
                logger.warning(f"Error while closing Redis connection: {e}")
    async def get_cache(self,cache_key):
        if not self.available:
            logger.warning(f"Redis is not available, cannot get cache for key: {cache_key}")
            return None
        try:
            cache_data = await self.client.get(cache_key)
            if cache_data is not None:
                logger.info(f"Cache hit for key: {cache_key}")
                cache_data = json.loads(cache_data)
                return cache_data
        except RedisError as e:
            logger.warning(f"Error while checking cache for key {cache_key}: {e}")
        logger.info(f"Cache miss for key: {cache_key}")
        return None
    async def set_cache(self, cache_key, cache_data,ttl=None):
        if not self.available:
            logger.warning(f"Redis is not available, cannot set cache for key: {cache_key}")
            return False
        try:
            cache_data = json.dumps(cache_data, ensure_ascii=False)
            if ttl is None:
                await self.client.set(cache_key, cache_data)
            else:
                await self.client.set(cache_key, cache_data, ex=ttl)
            logger.info(f"Cache set for key: {cache_key}")
            return True
        except RedisError as e:
            logger.warning(f"Error while setting cache for key {cache_key}: {e}")
        return False