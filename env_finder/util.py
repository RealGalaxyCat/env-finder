import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from colorama import Fore, Back, Style

from env_finder.github import get_file_content
from env_finder.analysis import analyze_env_file


TIMESTAMP_FOREGROUND_COLOR = Fore.WHITE

DATA_DIR = Path("/app/data")
HITS_FILE = DATA_DIR / "hits.json"
SECRETS_FILE = DATA_DIR / "secrets.json"
STATS_FILE = DATA_DIR / "stats.json"


DATA_DIR.mkdir(parents=True, exist_ok=True)
if not HITS_FILE.exists():
    print("Hits file doesn't exist, creating...")
    HITS_FILE.touch()
    HITS_FILE.write_text("[]", encoding="utf-8")

if not SECRETS_FILE.exists():
    print("Secrets file doesn't exist, creating...")
    SECRETS_FILE.touch()
    SECRETS_FILE.write_text("[]", encoding="utf-8")

if not STATS_FILE.exists():
    print("Stats file doesn't exist, creating...")
    STATS_FILE.touch()
    STATS_FILE.write_text("[]", encoding="utf-8")



def write_atomic(path: Path, data: dict | list | str | bytes):
    tmp = path.with_suffix(".tmp")
    match data:
        case dict() | list():
            tmp.write_text(json.dumps(data))
        case str():
            tmp.write_text(data)
        case bytes():
            tmp.write_bytes(data)
    tmp.rename(path)  # atomic on Linux/macOS, near-atomic on Windows




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



def log_stats(repos_scraped: int, secrets_count: int, errors_count: int):
    log(f"Repos scraped: {repos_scraped} - Secrets: {secrets_count} - Errors: {errors_count} ", ActionType.INFO, LogLevel.STATS)



def add_hits_entry(repo_name: str, branch: str, language: str, secrets: list[dict]):
    data = json.loads(HITS_FILE.read_text())

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

    write_atomic(HITS_FILE, data)



def add_secrets_entry(repo_name: str, branch: str, secrets: list[dict]):
    data = json.loads(SECRETS_FILE.read_text())

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

    write_atomic(SECRETS_FILE, data)


def add_stats_entry(entry: dict):
    data = json.loads(STATS_FILE.read_text("utf-8"))
    data.append(entry)
    write_atomic(STATS_FILE, data)
