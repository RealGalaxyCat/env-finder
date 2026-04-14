import os
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_PAT = os.getenv("GITHUB_PAT")
if not GITHUB_PAT:
    raise ValueError("'GITHUB_PAT' is not set.")


HEADERS = {"Authorization": f"token {GITHUB_PAT}"}

# TODO: handle unsuccessful responses everywhere
# TODO: Type Hint
def search_repos(query: str, page: int = 1, per_page: int = 100):
    url = f"https://api.github.com/search/repositories?q={query}&page={page}&per_page={per_page}"
    resp = requests.get(url, headers=HEADERS)
    if not resp.ok:
        return []

    return resp.json()



def get_files(repo_name) -> list[dict]:
    resp = requests.get(f"https://api.github.com/repos/{repo_name}", headers=HEADERS)
    print(resp.json().get("html_url"))
    if not resp.ok:
        return []

    branch = resp.json().get("default_branch", "main")

    tree_url = f"https://api.github.com/repos/{repo_name}/git/trees/{branch}?recursive=1"
    resp2 = requests.get(tree_url, headers=HEADERS)
    if not resp2.ok:
        return []

    return resp2.json()["tree"]



def get_file_content(repo_name: str, branch: str, filepath: str) -> str:
    resp = requests.get(f"https://raw.githubusercontent.com/{repo_name}/refs/heads/{branch}/{filepath}")
    if not resp.ok:
        return ""
    return resp.text



if __name__ == '__main__':
    print(get_files("thoeurnphen/POS_SYSTEM"))