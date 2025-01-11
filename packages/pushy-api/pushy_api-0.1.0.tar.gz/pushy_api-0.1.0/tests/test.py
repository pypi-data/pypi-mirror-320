import asyncio

import pytest

from pushy import PushyAPI, Feed, Notification

TESTING_FEED_API_KEY = 'akfd8ed4375485478a00'

@pytest.mark.asyncio
async def test_simple_notification():
    async with PushyAPI() as api:
        feed = Feed(api, TESTING_FEED_API_KEY)
        post = await feed.send_text("Hello, world!")
        assert post.post_key.startswith('pk')

@pytest.mark.asyncio
async def test_edit_notification():
    async with PushyAPI() as api:
        feed = Feed(api, TESTING_FEED_API_KEY)
        post_upd = await feed.send_text("Old text to be updated")
        await asyncio.sleep(1)
        await post_upd.edit_text("Updated text")

@pytest.mark.asyncio
async def test_delete_notification():
    async with PushyAPI() as api:
        feed = Feed(api, TESTING_FEED_API_KEY)
        post_del = await feed.send_text("Text to be deleted")
        await asyncio.sleep(1)
        await post_del.delete()