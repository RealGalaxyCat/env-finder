import logging
from env_finder.logger import getLogger
from env_finder.config import get_config

import ssl
import time
import httpx
import asyncio

from dotenv import load_dotenv
load_dotenv()

logger = getLogger(__name__)
for lib in ["httpx", "httpcore"]:
    getLogger(lib).setLevel(logging.WARNING)

_client: httpx.AsyncClient | None = None


def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            headers={"Authorization": f"token {get_config().github_pat}"},
            timeout=30.0,
            follow_redirects=True,   # requests does this by default; httpx does not
        )
    return _client


async def aclose_client() -> None:
    """Call once on shutdown to close the connection pool cleanly."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def _is_ssl_error(exc: BaseException | None) -> bool:
    seen = set()
    while exc is not None and id(exc) not in seen:
        seen.add(id(exc))
        if isinstance(exc, ssl.SSLError):
            return True
        exc = exc.__cause__ or exc.__context__
    return False



async def get(url: str, *, retries=5, **kwargs) -> httpx.Response | None:
    """
    Sends an HTTP request and handles retries when encountering a DNS resolution error (using exponential backoff) as well as Rate Limits.
    """
    client = _get_client()
    for attempt in range(retries):
        try:
            resp = await client.get(url, headers={"Authorization": f"token {get_config().github_pat}"}, **kwargs)

            # Handle Rate Limits
            retry_after = resp.headers.get("Retry-After")
            if resp.status_code in (403, 429):
                if resp.headers.get("X-RateLimit-Remaining") == "0":
                    reset = int(resp.headers["X-RateLimit-Reset"])
                    wait = max(reset - time.time(), 0) + 1

                    logger.warning(f"rate limit, sleeping {wait}s")
                    await asyncio.sleep(wait)
                    continue

                # Handle Secondary Rate Limits
                if retry_after:
                    wait = int(retry_after) + 1

                    logger.warning(f"secondary rate limit, sleeping {wait}s")
                    await asyncio.sleep(wait)
                    continue

            if resp.status_code == 401:
                raise RuntimeError("Invalid Github PAT (might be expired)")

            if resp.is_error:
                logger.error(resp.text)
                return None

            return resp

        except httpx.TransportError as e:
            if attempt == retries - 1:
                raise
            wait = 2 ** attempt
            if _is_ssl_error(e):
                logger.error(f"SSL error when trying to connect to '{url}' (attempt {attempt + 1}), retrying in {wait}s: {e}")
                logger.error("Maybe your Firewall is blocking the connection?")
            else:
                logger.error(f"connection/timeout error when trying to connect to '{url}' (attempt {attempt + 1}), retrying in {wait}s: {e}")
            await asyncio.sleep(wait)

    logger.error(f"exhausted {retries} retries for {url}")
    return None



async def search_repos(query: str, page: int = 1, per_page: int = 100) -> list[dict] | None:
    url = f"https://api.github.com/search/repositories?q={query}&page={page}&per_page={per_page}"
    try:
        resp = await get(url)
    except httpx.TransportError as e:
        logger.error(f"Error while searching for repos: {e}")
        return None
    if not resp:
        return None

    d = resp.json()
    count = d.get("total_count")
    logger.debug(f"[GITHUB] Found {count} matching repositories...")
    return d.get("items")



async def get_files(repo_name) -> list[dict] | None:
    try:
        resp = await get(f"https://api.github.com/repos/{repo_name}")
    except ConnectionError:
        return None
    if not resp:
        return None

    branch = resp.json().get("default_branch", "main")

    tree_url = f"https://api.github.com/repos/{repo_name}/git/trees/{branch}?recursive=1"
    try:
        resp2 = await get(tree_url)
    except httpx.TransportError:
        return None
    if not resp2:
        return None

    return resp2.json()["tree"]



async def get_file_content(repo_name: str, branch: str, filepath: str) -> str | None:
    try:
        resp = await get(f"https://raw.githubusercontent.com/{repo_name}/refs/heads/{branch}/{filepath}")
    except httpx.TransportError:
        return None
    if not resp:
        return None
    return resp.text


