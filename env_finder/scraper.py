from datetime import datetime, timezone, timedelta
from math import ceil
import time
import signal
from threading import Thread

from env_finder.github import get_files, search_repos
from env_finder.util import log, log_stats, LogLevel, ActionType, add_hits_entry, add_secrets_entry, add_stats_entry


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
        log("Received shutdown signal, shutting down...", ActionType.INFO, LogLevel.STATUS)


    def stats_loop(self):
        while self.running:
            ts = time.time()
            add_stats_entry({
                "timestamp": ts,
                "repos_scraped": self.repos_scraped,
                "secrets_count": self.secrets_count,
                "errors_count": self.errors_count
            })
            print("Added stats entry")
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

            log(f"[GITHUB] Querying '{query}'", ActionType.INFO, LogLevel.INFO)



            repos = search_repos(query, per_page=1)  # only 1, because we don't care about the actual repos just yet
            if not repos:
                log("Error while searching for repos", ActionType.ERROR, LogLevel.ERROR)
                log_stats(self.repos_scraped, self.secrets_count, self.errors_count)
                break

            count = repos["total_count"]

            log(f"[GITHUB] Found {count} matching repositories...", ActionType.INFO, LogLevel.INFO)

            # Split into chunks of 100 results each, because the Github API only allows up to 100 results per request
            for p in range(1, ceil(count/REPO_BATCH_SIZE) + 1):
                if not self.running:
                    break

                log(f"[GITHUB] Loading Page {p}/{ceil(count/REPO_BATCH_SIZE)}", ActionType.INFO, LogLevel.INFO)
                repos = search_repos(query, p, REPO_BATCH_SIZE)["items"]

                for repo in repos:
                    if not self.running:
                        break

                    name = repo["full_name"]
                    branch = repo.get("default_branch", "main")
                    language = repo.get("language")

                    if name in self.seen_repos:
                        log(f"[{name}] Repo was already searched, skipping", ActionType.INFO, LogLevel.INFO)
                        time.sleep(0.3)
                        continue

                    self.seen_repos.add(name)
                    time.sleep(0.5)


                    log(f"[{name}] Scraping ...  ".ljust(70), ActionType.INFO, LogLevel.INFO)

                    files = get_files(name)
                    if not files:
                        log(f"[{name}] Failed to fetch Files", ActionType.ERROR, LogLevel.ERROR)
                        self.errors_count += 1
                        time.sleep(5)
                        continue


                    secrets = []

                    for file in files:
                        path = file["path"]

                        if file["type"] == "tree": continue
                        if not file.get("size"): continue

                        if ".env" in path and not "example" in path:
                            secrets.append(file)


                    self.repos_scraped += 1
                    self.secrets_count += len(secrets)

                    if not secrets:
                        log(f"[{name}] No secrets found", ActionType.INFO, LogLevel.INFO)
                        continue


                    add_hits_entry(repo_name=name, branch=branch, language=language, secrets=secrets)
                    add_secrets_entry(repo_name=name, branch=branch, secrets=secrets)


            log_stats(self.repos_scraped, self.secrets_count, self.errors_count)




