from fastapi import FastAPI
import uvicorn
from threading import Thread

from api.api import app
from scraper import Scraper

API_PORT = 6768


def start_api(app: FastAPI):
    uvicorn.run(app, host="0.0.0.0", port=API_PORT)


def start_scraper():
    s = Scraper()
    s.start()



Thread(target=start_api, args=(app,)).start()
start_scraper()  # needs to run in main Thread so it can handle SIGINT/SIGTERM
