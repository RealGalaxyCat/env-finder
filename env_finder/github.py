import os
import time
import requests
from requests.exceptions import SSLError
from dotenv import load_dotenv

load_dotenv()

from env_finder.util import log, LogLevel, ActionType


GITHUB_PAT = os.getenv("GITHUB_PAT")
if not GITHUB_PAT:
    raise ValueError("'GITHUB_PAT' is not set.")

HEADERS = {"Authorization": f"token {GITHUB_PAT}"}




def get_with_dns_retry(url: str, *, retries=5, **kwargs) -> requests.Response | None:
    """
    Sends an HTTP request and handles retries when encountering a DNS resolution error using exponential backoff
    """
    for attempt in range(retries):
        try:
            return requests.get(url, headers=HEADERS, **kwargs)
        except requests.exceptions.ConnectionError as e:
            if attempt == retries - 1:
                raise
            wait = 2 ** attempt  # 1s, 2s, 4s, 8s
            log(f"DNS/connection error (attempt {attempt + 1}), retrying in {wait}s: {e}", ActionType.ERROR, LogLevel.ERROR)
            time.sleep(wait)




def search_repos(query: str, page: int = 1, per_page: int = 100):
    url = f"https://api.github.com/search/repositories?q={query}&page={page}&per_page={per_page}"
    try:
        resp = get_with_dns_retry(url)
    except SSLError:
        return []
    if not resp.ok:
        return []

    return resp.json()



def get_files(repo_name) -> list[dict]:
    try:
        resp = get_with_dns_retry(f"https://api.github.com/repos/{repo_name}")
    except SSLError:
        return []
    if not resp.ok:
        return []

    branch = resp.json().get("default_branch", "main")

    tree_url = f"https://api.github.com/repos/{repo_name}/git/trees/{branch}?recursive=1"
    try:
        resp2 = get_with_dns_retry(tree_url)
    except SSLError:
        return []
    if not resp2.ok:
        return []

    return resp2.json()["tree"]



def get_file_content(repo_name: str, branch: str, filepath: str) -> str:
    try:
        resp = get_with_dns_retry(f"https://raw.githubusercontent.com/{repo_name}/refs/heads/{branch}/{filepath}")
    except SSLError:
        return ""
    if not resp.ok:
        return ""
    return resp.text


