from datetime import datetime, timezone, timedelta

from dotenv import load_dotenv

from analysis import analyze_env_file
from github import get_files, search_repos, get_file_content

load_dotenv()

from math import ceil   
import time
from util import log

size = 100

seen = set()

# stats
repos_scraped = 0
secrets_found = 0
errors = 0


while True:
    basetime = datetime.now(timezone.utc)

    now = basetime - timedelta(minutes=1)
    before = now - timedelta(minutes=1)

    query = (f"stars:<5 "
             f"language:JavaScript "
             f"language:TypeScript "
             f"language:Python "
             f" created:{before.strftime("%Y-%m-%dT%H:%M:%SZ")}..{now.strftime("%Y-%m-%dT%H:%M:%SZ")}")

    log(f"Querying \"{query}\"")

    count = search_repos(query)["total_count"]
    log(f"Found {count} matching repositories...")

    for p in range(1, ceil(count/size) + 1):
        log(f"Loading Page {p}/{ceil(count/size)}")
        page = search_repos(query, p, size)

        for repo in page["items"]:

            name = repo["full_name"]
            branch = repo.get("default_branch", "main")
            language = repo.get("language")

            if name in seen:
                log("Already searched")
                time.sleep(0.3)
                continue

            seen.add(name)
            time.sleep(0.5)

            tmp = True
            while tmp:
                log(f"Scraping {name}...  ".ljust(70))

                try:
                    files = get_files(name)
                except:
                    log("Failed to fetch Files","error")
                    errors += 1
                    time.sleep(5)
                    continue

                tmp = False

            secrets = []

            for file in files:
                path: str = file["path"]

                if file["type"] == "tree": continue
                if file.get("size", 0) == 0: continue

                if ".env" in path and not "example" in path:
                    secrets.append(file)

            repos_scraped += 1

            if len(secrets) == 0:
                continue

            secrets_found += len(secrets)

            with open("hits.csv", "a") as f:
                log(f"Found Secrets for {name}", "results")

                for sec in secrets:
                    path = sec["path"]

                    f.write(f"{name},{branch},{language},https://github.com/{name}/blob/{branch}/{path},{sec["sha"]}\n")

            with open("secrets.csv", "a") as f:
                for sec in secrets:
                    path = sec["path"]

                    env_vars = analyze_env_file(get_file_content(name, branch, path))

                    for var in env_vars:
                        key = var.get("key")
                        val = var.get("value")
                        sev = var.get("severity")

                        if sev == "noise": continue

                        f.write(f"{name},{sev},{key},{val},https://github.com/{name}/blob/{branch}/{path}\n")


    log(f"Repos scraped: {repos_scraped} - Secrets: {secrets_found} - Errors: {errors} - ", "stats")