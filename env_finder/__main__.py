import asyncio
import sys
import logging
from fastapi import FastAPI
import uvicorn

from env_finder.api.api import app
from env_finder.scraper import Scraper
from env_finder.logger import setup_logger, getLogger

setup_logger(logging.DEBUG, "logs.log")
logger = getLogger(__name__)


async def start_api(app: FastAPI):
    config = uvicorn.Config(app, host="0.0.0.0", port=6767)
    server = uvicorn.Server(config)
    await server.serve()


async def start_scraper():
    try:
        await Scraper().start()
    except Exception as e:
        logger.fatal(e)
        sys.exit(1)


async def main():
    await asyncio.gather(start_scraper(), start_api(app))

asyncio.run(main())