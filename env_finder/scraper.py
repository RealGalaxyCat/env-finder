from datetime import datetime, timezone, timedelta
from math import ceil
import time
import signal
from threading import Thread

from env_finder.github import get_files, search_repos, get_file_content
from env_finder.util import log_stats, add_hits_entry, add_secrets_entry, heartbeat
from env_finder.logger import getLogger

logger = getLogger(__name__)

REPO_BATCH_SIZE = 100


class Scraper:
    def __init__(self):
        self.start_time_ms = None
        self.start_time_ts = None

        self.repos_scraped = 0
        self.env_files_found = 0
        # self.secrets_found = 0
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
            heartbeat(
                timestamp=ts,
                up_since_epoch_ms=self.start_time_ms,
                repos_scraped=self.repos_scraped,
                env_files_found=self.env_files_found,
                errors=self.errors_count
            )
            log_stats(self.repos_scraped, self.env_files_found, self.errors_count)
            time.sleep(8)


    def start(self):
        self.start_time_ms = time.time()
        self.start_time_ts = datetime.fromtimestamp(self.start_time_ms).strftime('%Y-%m-%d %H:%M:%S')

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
                log_stats(self.repos_scraped, self.env_files_found, self.errors_count)
                break

            count = len(repos)
            # Split into chunks of 100 results each, because the Github API only allows up to 100 results per request
            for p in range(1, ceil(count/REPO_BATCH_SIZE) + 1):
                if not self.running:
                    break

                logger.info(f"[GITHUB] Loading Page {p}/{ceil(count/REPO_BATCH_SIZE)}")
                repos = search_repos(query, p, REPO_BATCH_SIZE)

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

                    env_files = []
                    for file in files:
                        path = file["path"]

                        if file["type"] == "tree": continue
                        if not file.get("size"): continue

                        filename = path.rsplit("/", 1)[-1]
                        if filename.endswith(".env") and not any(i in filename for i in ["example", "template", ".xcode"]):   # .xcode.env
                            env_files.append(file)


                    self.repos_scraped += 1
                    self.env_files_found += len(env_files)

                    if not env_files:
                        logger.info(f"[{name}] No env files found")
                        continue


                    add_hits_entry(repo_name=name, branch=branch, language=language, secrets=env_files)
                    for sec in env_files:
                        path = sec["path"]
                        file_content = get_file_content(name, branch, path)
                        if file_content:
                            add_secrets_entry(repo_name=name, branch=branch, path=path, file_content=file_content)


