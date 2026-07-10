import sys
import logging
from fastapi import FastAPI
import uvicorn
from threading import Thread

from env_finder.api.api import app
from env_finder.scraper import Scraper
from env_finder.logger import setup_logger, getLogger
from env_finder.errors import GithubAuthError

setup_logger(logging.DEBUG, "logs.log")
logger = getLogger(__name__)


def start_api(app: FastAPI):
    uvicorn.run(app, host="0.0.0.0", port=6767)


def start_scraper():
    try:
        s = Scraper()
        s.start()
    except GithubAuthError as e:
        logger.fatal(e)
        sys.exit(1)

Thread(target=start_api, args=(app,)).start()
start_scraper()  # needs to run in main Thread so it can handle SIGINT/SIGTERM
