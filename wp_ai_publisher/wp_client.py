from __future__ import annotations
import time
from urllib.parse import quote
import requests
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential
from .config import Site
from .errors import WordPressError

def _transient(exc): return isinstance(exc, (requests.RequestException, WordPressError)) and (not isinstance(exc, WordPressError) or "HTTP 429" in str(exc) or "HTTP 5" in str(exc))

class WordPressClient:
    def __init__(self, site: Site, retries: int = 3, rpm: int = 20, allow_insecure: bool = False):
        if not allow_insecure and not site.base_url.startswith("https://"): raise WordPressError("Refusing non-HTTPS WordPress URL; pass --allow-insecure to override")
        self.site, self.retries, self.interval = site, retries, 60 / rpm
        self.session = requests.Session()
        if site.credentials: self.session.auth = (site.credentials.username, site.credentials.app_password)
        self.cache = {}; self._last_request = 0.0

    @retry(retry=retry_if_exception(_transient), stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=20), reraise=True)
    def request(self, method, path, **kwargs):
        if not self.site.credentials: raise WordPressError(f"Missing credentials for {self.site.id}")
        delay = self.interval - (time.monotonic() - self._last_request)
        if delay > 0: time.sleep(delay)
        response = self.session.request(method, self.site.base_url.rstrip("/") + path, timeout=30, **kwargs)
        self._last_request = time.monotonic()
        if response.status_code >= 400: raise WordPressError(f"HTTP {response.status_code}: {response.text[:300]}")
        return response

    def term_id(self, taxonomy: str, name: str) -> int:
        key = (taxonomy, name.casefold())
        if key in self.cache: return self.cache[key]
        path = f"/wp-json/wp/v2/{taxonomy}?search={quote(name)}"
        found = next((x for x in self.request("GET", path).json() if x["name"].casefold() == name.casefold()), None)
        item = found or self.request("POST", f"/wp-json/wp/v2/{taxonomy}", json={"name": name}).json()
        self.cache[key] = item["id"]; return item["id"]

    def post_payload(self, article, html, categories, tags):
        payload = {"title": article.title, "content": html, "status": self.site.default_status, "excerpt": article.excerpt, "categories": categories, "tags": tags}
        if self.site.seo_plugin == "yoast": payload["meta"] = {"_yoast_wpseo_focuskw": article.focus_keyword, "_yoast_wpseo_metadesc": article.meta_description}
        elif self.site.seo_plugin == "rankmath": payload["meta"] = {"rank_math_focus_keyword": article.focus_keyword, "rank_math_description": article.meta_description}
        return payload

    def create_post(self, payload): return self.request("POST", "/wp-json/wp/v2/posts", json=payload).json()

    def validate_mu_plugin(self):
        return self.request("GET", "/wp-json/ai-publisher/v1/seo-meta/1").status_code
