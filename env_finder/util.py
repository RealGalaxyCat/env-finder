import json
from pathlib import Path

from env_finder.analysis import analyze_env_file
from env_finder.logger import getLogger

logger = getLogger(__name__)


DATA_DIR = Path("/app/data")
HITS_FILE = DATA_DIR / "hits.json"
SECRETS_FILE = DATA_DIR / "secrets.json"
HEALTH_FILE = DATA_DIR / "health.json"


DATA_DIR.mkdir(parents=True, exist_ok=True)
if not HITS_FILE.exists():
    print("Hits file doesn't exist, creating...")
    HITS_FILE.touch()
    HITS_FILE.write_text("[]", encoding="utf-8")

if not SECRETS_FILE.exists():
    print("Secrets file doesn't exist, creating...")
    SECRETS_FILE.touch()
    SECRETS_FILE.write_text("[]", encoding="utf-8")

if not HEALTH_FILE.exists():
    print("Stats file doesn't exist, creating...")
    HEALTH_FILE.touch()



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




def log_stats(repos_scraped: int, secret_files_count: int, errors_count: int):
    logger.info("# " + "~"*40 + " #")
    logger.info(f"Repos scraped: {repos_scraped} - Secrets files: {secret_files_count} - Errors: {errors_count} ")
    logger.info("# " + "~"*40 + " #")



def add_hits_entry(repo_name: str, branch: str, language: str, secrets: list[dict]):
    data = json.loads(HITS_FILE.read_text())

    logger.secret(f"[{repo_name}] Found {len(secrets)} Secret(s)")

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



def add_secrets_entry(repo_name: str, branch: str, path: str, file_content: str):
    data = json.loads(SECRETS_FILE.read_text())
    env_vars = analyze_env_file(file_content)

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


def heartbeat(timestamp: float, up_since_epoch_ms: float, repos_scraped: int, errors: int, env_files_found: int):
    HEALTH_FILE.write_text(json.dumps({
        "timestamp": timestamp,
        "up_since": up_since_epoch_ms,
        "stats" : {
            "repos_scraped": repos_scraped,
            "errors": errors,
            "env_files_found": env_files_found
        }
    }), encoding="utf-8")
