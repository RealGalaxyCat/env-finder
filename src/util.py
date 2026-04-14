import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from colorama import Fore, Back, Style

from github import get_file_content
from analysis import analyze_env_file


TIMESTAMP_FOREGROUND_COLOR = Fore.WHITE

HITS_FILE = Path(__file__).parent.parent / "data" / "hits.json"
SECRETS_FILE = Path(__file__).parent.parent / "data" / "secrets.json"

if not HITS_FILE.exists():
    print("Hits file doesn't exist, creating...")
    HITS_FILE.touch()
    HITS_FILE.write_text("[]", encoding="utf-8")

if not SECRETS_FILE.exists():
    print("Secrets file doesn't exist, creating...")
    SECRETS_FILE.touch()
    SECRETS_FILE.write_text("[]", encoding="utf-8")




class LogLevel(Enum):
    INFO = ("info", Back.LIGHTCYAN_EX, Fore.BLACK)
    ERROR = ("error", Back.RED, Fore.BLACK)
    RESULTS = ("results", Back.YELLOW, Fore.BLACK)
    STATS = ("stats", Back.LIGHTGREEN_EX, Fore.BLACK)

    def __init__(self, name_: str, background_color: str, foreground_color: type[Fore]):
        self.name_ = name_
        self.bg_color = background_color
        self.fg_color = foreground_color


def log(message: str, level: LogLevel = LogLevel.INFO, end="\n"):
    ts = f"{TIMESTAMP_FOREGROUND_COLOR}[{datetime.now().strftime("%H:%M:%S")}]{Fore.RESET}"
    print(f"{ts} {level.bg_color}{level.fg_color}[{level.name_.ljust(10)}]{Style.RESET_ALL} {message}", end=end)




def add_hits_entry(repo_name: str, branch: str, language: str, secrets: list[dict]):
    with open(HITS_FILE, "r") as f:
        data = json.load(f)

    log(f"[{repo_name}] [+] Found {len(secrets)} Secrets", LogLevel.RESULTS)

    for sec in secrets:
        path = sec["path"]

        data.append({
            "repo_name": repo_name,
            "branch": branch,
            "language": language,
            "url" : f"https://github.com/{repo_name}/blob/{branch}/{path}",
            "sha" : sec["sha"]
        })

    with open(HITS_FILE, "w") as f:
        json.dump(data, f, indent=4)



def add_secrets_entry(repo_name: str, branch: str, secrets: list[dict]):
    with open(SECRETS_FILE, "r") as f:
        data = json.load(f)

    for sec in secrets:
        path = sec["path"]

        env_vars = analyze_env_file(get_file_content(repo_name, branch, path))

        for var in env_vars:
            if var.get("severity") == "noise": continue

            data.append({
                "repo_name": repo_name,
                "url" : f"https://github.com/{repo_name}/blob/{branch}/{path}",
                "severity" : var.get("severity"),
                "key" : var.get("key"),
                "value" : var.get("value")
            })

    with open(SECRETS_FILE, "w") as f:
        json.dump(data, f, indent=4)

