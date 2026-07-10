import os
import time
import requests
from requests.exceptions import SSLError

from dotenv import load_dotenv
load_dotenv()

from env_finder.logger import getLogger
from env_finder.errors import GithubAuthError

logger = getLogger(__name__)


GITHUB_PAT = os.getenv("GITHUB_PAT")
if not GITHUB_PAT:
    raise GithubAuthError("Missing Github PAT (check 'GITHUB_PAT' env variable)")

HEADERS = {"Authorization": f"token {GITHUB_PAT}"}




def get(url: str, *, retries=5, **kwargs) -> requests.Response | None:
    """
    Sends an HTTP request and handles retries when encountering a DNS resolution error (using exponential backoff) as well as Rate Limits.
    """
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, **kwargs)


            # Handle Rate Limits
            retry_after = resp.headers.get("Retry-After")
            if resp.status_code in (403, 429):
                if resp.headers.get("X-RateLimit-Remaining") == "0":
                    reset = int(resp.headers["X-RateLimit-Reset"])
                    wait = max(reset - time.time(), 0) + 1

                    logger.warning(f"rate limit, sleeping {wait}s")
                    time.sleep(wait)
                    continue

                # Handle Secondary Rate Limits
                if retry_after:
                    wait = int(retry_after) + 1

                    logger.warning(f"secondary rate limit, sleeping {wait}s")
                    time.sleep(wait)
                    continue

            if resp.status_code == 401:
                raise GithubAuthError("Invalid Github PAT (might be expired)")

            if not resp.ok:
                logger.error(resp.text)
                return None

            return resp

        except SSLError as e:
            if attempt == retries - 1:
                raise
            wait = 2 ** attempt
            logger.error(f"SSL error when trying to connect to '{url}' (attempt {attempt + 1}), retrying in {wait}s: {e}")
            logger.error("Maybe your Firewall is blocking the connection?")
            time.sleep(wait)

        except requests.exceptions.ConnectionError as e:
            if attempt == retries - 1:
                raise
            wait = 2 ** attempt  # 1s, 2s, 4s, 8s
            logger.error(f"DNS/connection error when trying to connect to '{url}' (attempt {attempt + 1}), retrying in {wait}s: {e}")
            time.sleep(wait)

    logger.error(f"exhausted {retries} retries for {url}")
    return None



def search_repos(query: str, page: int = 1, per_page: int = 100) -> list[dict] | None:
    url = f"https://api.github.com/search/repositories?q={query}&page={page}&per_page={per_page}"
    try:
        resp = get(url)
    except ConnectionError as e:
        logger.error(f"Error while searching for repos: {e}")
        return {}

    d = resp.json()
    count = d.get("total_count")
    logger.debug(f"[GITHUB] Found {count} matching repositories...")
    return d.get("items")



def get_files(repo_name) -> list[dict] | None:
    try:
        resp = get(f"https://api.github.com/repos/{repo_name}")
    except ConnectionError:
        return None
    if not resp.ok:
        return None

    branch = resp.json().get("default_branch", "main")

    tree_url = f"https://api.github.com/repos/{repo_name}/git/trees/{branch}?recursive=1"
    try:
        resp2 = get(tree_url)
    except ConnectionError:
        return None
    if not resp2.ok:
        logger.error(resp.text)
        return None

    return resp2.json()["tree"]



def get_file_content(repo_name: str, branch: str, filepath: str) -> str | None:
    try:
        resp = get(f"https://raw.githubusercontent.com/{repo_name}/refs/heads/{branch}/{filepath}")
    except ConnectionError:
        return None
    if not resp.ok:
        logger.error(resp.text)
        return None
    return resp.text


