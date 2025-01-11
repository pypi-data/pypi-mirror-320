import aiohttp
import lxml.html
from markdownify import markdownify as md
from typing import Optional, Union
from .typing import QueryType, ResponseStream


class Client:
    async def ask(self, query: QueryType) -> ResponseStream:
        async with aiohttp.ClientSession(base_url="https://iask.ai/") as session:
            async with session.get(
                "/",
                params=(
                    {"mode": "question", "q": query}
                    if isinstance(query, str)
                    else query
                ),
            ) as response:
                etree = lxml.html.fromstring(await response.text())
                phx_node = etree.xpath('//*[starts-with(@id, "phx-")]').pop()
                csrf_node = etree.xpath('//*[@name="csrf-token"]').pop()
                async with session.ws_connect(
                    "/live/websocket",
                    params={"_csrf_token": csrf_node.get("content"), "vsn": "2.0.0"},
                ) as wsResponse:
                    await wsResponse.send_json(
                        [
                            None,
                            None,
                            f"lv:{phx_node.get('id')}",
                            "phx_join",
                            {
                                "url": str(response.url),
                                "session": phx_node.get("data-phx-session"),
                            },
                        ]
                    )
                    while json := await wsResponse.receive_json():
                        diff: dict = json[4]
                        try:
                            chunk: str = diff["e"][0][1]["data"]
                            yield chunk.replace("<br/>", "\n")
                        except:
                            if cache := self._cache_find(diff):
                                if diff.get("response", None):
                                    yield cache
                                break

    def _cache_find(self, diff: Union[dict, list]) -> Optional[str]:
        values = diff if isinstance(diff, list) else diff.values()
        for value in values:
            if isinstance(value, (list, dict)):
                if cache := self._cache_find(value):
                    return cache
            if isinstance(value, str) and value.startswith("<p>"):
                return md(value).strip()

        return None
