import asyncio

import httpx

from app.main import app


def test_root_renders_index_template():
    async def get_root() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
            return await client.get("/")

    response = asyncio.run(get_root())

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<title>Text generator</title>" in response.text
    assert "<h3>LLM Test</h3>" in response.text
