from datetime import datetime, timezone, timedelta
from math import ceil
import time
import signal
from threading import Thread

from env_finder.github import get_files, search_repos, get_file_content
from env_finder.util import log_stats, add_hits_entry, add_secrets_entry, add_stats_entry
from env_finder.logger import getLogger

logger = getLogger(__name__)

REPO_BATCH_SIZE = 100


class Scraper:
    def __init__(self):
        self.repos_scraped = 0
        self.secrets_count = 0
        self.errors_count = 0
        self.running = False

        self.seen_repos = set()

        signal.signal(signal.SIGTERM, self.handle_stop_signals)
        signal.signal(signal.SIGINT, self.handle_stop_signals)


    def handle_stop_signals(self, *_):
        self.running = False
        logger.info("Received shutdown signal, shutting down...")


    def stats_loop(self):
        while self.running:
            ts = time.time()
            add_stats_entry({
                "timestamp_ms": ts,
                "repos_scraped": self.repos_scraped,
                "secrets_count": self.secrets_count,
                "errors_count": self.errors_count
            })
            time.sleep(8)


    def start(self):
        self.running = True
        Thread(target=self.stats_loop).start()

        while self.running:
            now = datetime.now(timezone.utc)

            to = now - timedelta(minutes=1)
            from_ = to - timedelta(minutes=1)

            query = (f"stars:<5 "
                     f"language:JavaScript "
                     f"language:TypeScript "
                     f"language:Python "
                     f" created:{from_.strftime("%Y-%m-%dT%H:%M:%SZ")}..{to.strftime("%Y-%m-%dT%H:%M:%SZ")}")

            logger.info(f"[GITHUB] Querying '{query}'")



            repos = search_repos(query, per_page=1)  # only 1, because we don't care about the actual repos just yet
            if not repos:
                logger.error("Error while searching for repos")
                log_stats(self.repos_scraped, self.secrets_count, self.errors_count)
                break

            count = repos["total_count"]

            logger.info(f"[GITHUB] Found {count} matching repositories...")

            # Split into chunks of 100 results each, because the Github API only allows up to 100 results per request
            for p in range(1, ceil(count/REPO_BATCH_SIZE) + 1):
                if not self.running:
                    break

                logger.info(f"[GITHUB] Loading Page {p}/{ceil(count/REPO_BATCH_SIZE)}")
                repos = search_repos(query, p, REPO_BATCH_SIZE)["items"]

                for repo in repos:
                    if not self.running:
                        break

                    name = repo["full_name"]
                    branch = repo.get("default_branch", "main")
                    language = repo.get("language")

                    if name in self.seen_repos:
                        logger.debug(f"[{name}] Repo was already searched, skipping")
                        time.sleep(0.3)
                        continue

                    self.seen_repos.add(name)
                    time.sleep(0.5)


                    logger.info(f"[{name}] Scraping ...  ".ljust(70))

                    files = get_files(name)
                    if not files:
                        logger.error(f"[{name}] Failed to fetch Files")
                        self.errors_count += 1
                        time.sleep(5)
                        continue


                    secrets = []

                    for file in files:
                        path = file["path"]

                        if file["type"] == "tree": continue
                        if not file.get("size"): continue

                        filename = path.rsplit("/", 1)[-1]
                        if filename.endswith(".env") and not any(i in filename for i in ["example", "template", ".xcode"]):   # .xcode.env
                            secrets.append(file)


                    self.repos_scraped += 1
                    self.secrets_count += len(secrets)

                    if not secrets:
                        logger.info(f"[{name}] No secrets found")
                        continue


                    add_hits_entry(repo_name=name, branch=branch, language=language, secrets=secrets)
                    for sec in secrets:
                        path = sec["path"]
                        add_secrets_entry(repo_name=name, branch=branch, path=path, file_content=get_file_content(name, branch, path))


            log_stats(self.repos_scraped, self.secrets_count, self.errors_count)




