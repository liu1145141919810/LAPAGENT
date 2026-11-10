import pytest

from Webcrawl.webcrawl import WebCrawl

@pytest.mark.asyncio
async def test_search_against_live_searxng():
    """Optional integration test; expects SearXNG reachable at configured URL."""
    searxng = WebCrawl()
    result = await searxng.search("FastAPI Python", max_results=3)

    assert "error" not in result, result
    assert isinstance(result.get("results"), list)
    assert len(result["results"]) <= 3
    for item in result["results"]:
        assert item["title"]
        assert item["url"].startswith(("http://", "https://"))
        assert isinstance(item["snippet"], str)