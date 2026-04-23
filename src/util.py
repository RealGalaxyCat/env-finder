import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from colorama import Fore, Back, Style

from github import get_file_content
from analysis import analyze_env_file


TIMESTAMP_FOREGROUND_COLOR = Fore.WHITE

BASE = Path(__file__).parent.parent
DATA_DIR = BASE / "data"
HITS_FILE = DATA_DIR / "hits.json"
SECRETS_FILE = DATA_DIR / "secrets.json"

DATA_DIR.mkdir(parents=True, exist_ok=True)
if not HITS_FILE.exists():
    print("Hits file doesn't exist, creating...")
    HITS_FILE.touch()
    HITS_FILE.write_text("[]", encoding="utf-8")

if not SECRETS_FILE.exists():
    print("Secrets file doesn't exist, creating...")
    SECRETS_FILE.touch()
    SECRETS_FILE.write_text("[]", encoding="utf-8")





RESET = Style.RESET_ALL


class LogLevel(Enum):
    INFO    = ("info",    Back.CYAN,    Fore.BLACK)
    ERROR   = ("error",   Back.RED,     Fore.WHITE)
    RESULTS = ("results", Back.YELLOW, Fore.WHITE)
    STATS   = ("stats",   Back.GREEN,   Fore.BLACK)
    STATUS  = ("status",  Back.BLUE,    Fore.WHITE)

    def __init__(self, name_: str, background_color: str, foreground_color: str):
        self.name_ = name_.upper()
        self.bg_color = background_color
        self.fg_color = foreground_color


class ActionType(Enum):
    SUCCESS = ("[+]", None,      Fore.GREEN)
    ERROR   = ("[-]", Back.RED,  Fore.BLACK)
    DEBUG   = ("[~]", None,      Fore.CYAN)
    INFO    = ("[*]", None,      Fore.BLUE)
    WARNING = ("[!]", None,      Fore.YELLOW)

    def __init__(self, text: str, foreground_color: str, background_color: str):
        self.text = text
        self.fg = foreground_color
        self.bg = background_color




def log(message: str, at: ActionType, level: LogLevel = LogLevel.INFO, end="\n"):
    ts = f"{TIMESTAMP_FOREGROUND_COLOR}[{datetime.now().strftime("%H:%M:%S")}]{Fore.RESET}"
    if not at:
        action_text = ""
    else:
        action_text = at.text

    level_bg = level.bg_color if level.bg_color else ""
    level_fg = level.fg_color if level.fg_color else ""
    at_bg = at.bg if at.bg else ""
    at_fg = at.fg if at.fg else ""
    print(f"{ts} {level_bg}{level_fg}[{level.name_.ljust(7)}]{RESET} {at_bg}{at_fg}{action_text}{RESET} {message}", end=end)




def add_hits_entry(repo_name: str, branch: str, language: str, secrets: list[dict]):
    with open(HITS_FILE, "r") as f:
        data = json.load(f)

    log(f"[{repo_name}] Found {len(secrets)} Secret(s)", ActionType.SUCCESS, LogLevel.RESULTS)

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

