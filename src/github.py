import os

import requests
from dotenv import load_dotenv

load_dotenv()

HEADERS = {"Authorization": f"token {os.getenv("GITHUB_PAT")}"}

def search_repos(searchstring: str, page: int = 1, per_page: int = 1):
    url = f"https://api.github.com/search/repositories?q={searchstring}&page={page}&per_page={per_page}"

    return requests.get(url, headers=HEADERS).json()

def get_files(repo_name):
    repo_res = requests.get(f"https://api.github.com/repos/{repo_name}", headers=HEADERS)

    if repo_res.status_code != 200: return []

    repo_data = repo_res.json()
    branch = repo_data.get("default_branch", "main")

    tree_url = f"https://api.github.com/repos/{repo_name}/git/trees/{branch}?recursive=1"
    tree_res = requests.get(tree_url, headers=HEADERS)

    if tree_res.status_code != 200: return []

    return tree_res.json()["tree"]

def get_file_content(repo, branch, filepath):
    res = requests.get(f"https://raw.githubusercontent.com/{repo}/refs/heads/{branch}/{filepath}")

    return res.text

if __name__ == '__main__':
    print(get_files("thoeurnphen/POS_SYSTEM"))