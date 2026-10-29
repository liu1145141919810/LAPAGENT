import http
from urllib.parse import urlparse

from public.logger import setup_logger
logger = setup_logger(__name__)

class WebCrawl:
    def __init__(self):
        pass

    def _validate_url(self, url: str) -> bool:
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            logger.error(f"Invalid URL scheme: {parsed.scheme}")
            return False
        if not parsed.hostname:
            logger.error(f"Invalid URL hostname: {parsed.hostname}")
            return False
        return True
    
    def search(self):
        pass