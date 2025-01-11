from .typing import ResponseStream


async def buffer(stream: ResponseStream):
    buffer = ""
    async for chunk in stream:
        buffer += chunk
    return buffer
