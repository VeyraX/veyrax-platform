import redis
import os
import time
import uuid
from contextlib import contextmanager
from typing import Optional
import logging

redis_client = redis.Redis.from_url(
    os.environ.get("REDIS_URL", "redis://localhost:6379"),
    decode_responses=True
)

@contextmanager
def redis_lock(lock_name: str, timeout: int = 30, poll_interval: float = 0.1, lock_expiry: Optional[int] = None):
    identifier = str(uuid.uuid4())
    lock_key = f"lock:{lock_name}"
    
    if lock_expiry is None:
        lock_expiry = timeout - 10
    
    acquired = False
    try:
        end_time = time.time() + timeout
        while time.time() < end_time:
            if redis_client.set(lock_key, identifier, nx=True, ex=lock_expiry):
                acquired = True
                break
            time.sleep(poll_interval)
        
        if not acquired:
            raise TimeoutError(f"Could not acquire lock {lock_name} within {timeout} seconds")
        
        yield
        
    finally:
        if acquired:
            try:
                pipe = redis_client.pipeline()
                pipe.watch(lock_key)
                current_value = pipe.get(lock_key)
                if current_value == identifier:
                    pipe.multi()
                    pipe.delete(lock_key)
                    pipe.execute()
                else:
                    pipe.unwatch()
            except Exception as e:
                logging.warning(f"Error releasing lock {lock_name}: {e}") 