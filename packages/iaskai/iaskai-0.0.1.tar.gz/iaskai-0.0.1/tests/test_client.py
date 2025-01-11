import iask
import pytest

@pytest.mark.asyncio
async def test_client():
    client = iask.Client()
    async for chunk in client.ask('Who is Yugi?'):
        assert isinstance(chunk, str)
        break