import httpx
import os
from urllib.parse import urlparse
import configparser

from public.logger import setup_logger

logger = setup_logger(__name__)
_current_dir = os.path.dirname(os.path.abspath(__file__))
_config_path = os.path.join(_current_dir, '..', 'public', 'public_config.ini')
cfg = configparser.ConfigParser()
cfg.read(_config_path)

DEFAULT_SEARXNG_URL = "http://localhost:8080"

class WebCrawl:
    def __init__(self, base_url=None):
        configured_url = cfg.get("Web", "web_url", fallback=None)
        self.url = (
            base_url
            or os.getenv("LAPAGENT_SEARXNG_URL")
            or configured_url
            or DEFAULT_SEARXNG_URL
        ).rstrip("/")
        logger.info("WebCrawl initialized")

    def _validate_url(self, url: str) -> bool:
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            logger.error(f"Invalid URL scheme: {parsed.scheme}")
            return False
        if not parsed.hostname:
            logger.error(f"Invalid URL hostname: {parsed.hostname}")
            return False
        return True
    
    async def search(
            self, 
            query: str, 
            max_results: int = 5,
            max_title_length: int = 100,
            max_snippet_length: int = 200,
    ) -> dict:
        if not isinstance(query, str) or not query.strip():
            logger.error("Invalid query")
            return {"error": "Invalid query"}
        query = query.strip()

        try:
            timeout = httpx.Timeout(10.0,connect=3.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(
                    f"{self.url}/search",
                    params={
                        "q":query,
                        "format":"json",
                        "categories":"general",
                    },
                    headers={"Accept": "application/json"}
                )
                response.raise_for_status()
                data = response.json()
            
        except httpx.TimeoutException:
            logger.warning("SearXNG search request timed out")
            return {"error": "Search service timed out"}
        except httpx.HTTPStatusError as exc:
            logger.warning("SearXNG returned HTTP %s", exc.response.status_code)
            return {"error": "Search service returned an error"}
        except httpx.RequestError as exc:
            logger.warning("SearXNG request failed: %s", type(exc).__name__)
            return {"error": "Could not connect to search service"}
        except ValueError:
            logger.warning("SearXNG returned invalid JSON")
            return {"error": "Search service returned an invalid response"}
        if not isinstance(data, dict) or not isinstance(data.get("results"), list):
            logger.warning("SearXNG response has an unexpected shape")
            return {"error": "Search service returned an invalid response"}
        
        results=[]
        for item in data.get("results", [])[:max_results]:
            title = item.get("title")
            url = item.get("url")
            snippet = item.get("content")
            if not isinstance(url, str) or not self._validate_url(url):
                continue
            results.append({
                "title":title[:max_title_length] if isinstance(title, str) else "",
                "url":url,
                "snippet": snippet[:max_snippet_length] if isinstance(snippet, str) else ""
            })

        return {"results": results}