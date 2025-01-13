import asyncio
import logging
import time

from zyjj_client_sdk.lib.cache import Cache
import pytest

cache = Cache()

def get_data():
    logging.info('get data')
    time.sleep(1)
    return 1

@pytest.mark.asyncio
async def test_get_lock():
    task1 = cache.get_data('a', get_data)
    task2 = cache.get_data('a', get_data)
    await asyncio.gather(task1, task2)
