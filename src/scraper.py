from datetime import datetime, timezone, timedelta
from math import ceil
import time

from github import get_files, search_repos
from util import log, LogLevel, add_hits_entry, add_secrets_entry


size = 100

seen = set()

# stats
repos_scraped = 0
secrets_found = 0
errors = 0


while True:
    now = datetime.now(timezone.utc)

    to = now - timedelta(minutes=1)
    from_ = to - timedelta(minutes=1)

    query = (f"stars:<5 "
             f"language:JavaScript "
             f"language:TypeScript "
             f"language:Python "
             f" created:{from_.strftime("%Y-%m-%dT%H:%M:%SZ")}..{to.strftime("%Y-%m-%dT%H:%M:%SZ")}")

    log(f"[GITHUB] Querying '{query}'")



    repos = search_repos(query, per_page=1)  # only 1, because we dont care about the actual repos just yet
    if not repos:
        log("Error while searching for repos", LogLevel.ERROR)
        log(f"Repos scraped: {repos_scraped} - Secrets: {secrets_found} - Errors: {errors} - ", LogLevel.STATS)
        break

    count = repos["total_count"]

    log(f"[GITHUB] Found {count} matching repositories...")

    # Split into chunks of 100 results each, because the Github API only allows up to 100 results per request
    for p in range(1, ceil(count/size) + 1):
        log(f"[GITHUB] Loading Page {p}/{ceil(count/size)}")
        repos = search_repos(query, p, size)["items"]

        for repo in repos:
            name = repo["full_name"]
            branch = repo.get("default_branch", "main")
            language = repo.get("language")

            if name in seen:
                log(f"[{name}] [~] Repo was already searched, skipping")
                time.sleep(0.3)
                continue

            seen.add(name)
            time.sleep(0.5)


            log(f"[{name}] [~] Scraping ...  ".ljust(70))

            files = get_files(name)
            if not files:
                log(f"[{name}] [-] Failed to fetch Files", LogLevel.ERROR)
                errors += 1
                time.sleep(5)
                continue


            secrets = []

            for file in files:
                path = file["path"]

                if file["type"] == "tree": continue
                if not file.get("size"): continue

                if ".env" in path and not "example" in path:
                    secrets.append(file)


            repos_scraped += 1
            secrets_found += len(secrets)

            if not secrets:
                log(f"[{name}] [-] No secrets found")
                continue


            add_hits_entry(repo_name=name, branch=branch, language=language, secrets=secrets)
            add_secrets_entry(repo_name=name, branch=branch, secrets=secrets)


    log(f"Repos scraped: {repos_scraped} - Secrets: {secrets_found} - Errors: {errors} - ", LogLevel.STATS)




