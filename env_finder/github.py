import os
import requests
from requests.exceptions import SSLError
from dotenv import load_dotenv

load_dotenv()

GITHUB_PAT = os.getenv("GITHUB_PAT")
if not GITHUB_PAT:
    raise ValueError("'GITHUB_PAT' is not set.")

HEADERS = {"Authorization": f"token {GITHUB_PAT}"}


def search_repos(query: str, page: int = 1, per_page: int = 100):
    url = f"https://api.github.com/search/repositories?q={query}&page={page}&per_page={per_page}"
    try:
        resp = requests.get(url, headers=HEADERS)
    except SSLError:
        return []
    if not resp.ok:
        return []

    return resp.json()



def get_files(repo_name) -> list[dict]:
    try:
        resp = requests.get(f"https://api.github.com/repos/{repo_name}", headers=HEADERS)
    except SSLError:
        return []
    if not resp.ok:
        return []

    branch = resp.json().get("default_branch", "main")

    tree_url = f"https://api.github.com/repos/{repo_name}/git/trees/{branch}?recursive=1"
    try:
        resp2 = requests.get(tree_url, headers=HEADERS)
    except SSLError:
        return []
    if not resp2.ok:
        return []

    return resp2.json()["tree"]



def get_file_content(repo_name: str, branch: str, filepath: str) -> str:
    try:
        resp = requests.get(f"https://raw.githubusercontent.com/{repo_name}/refs/heads/{branch}/{filepath}")
    except SSLError:
        return ""
    if not resp.ok:
        return ""
    return resp.text


