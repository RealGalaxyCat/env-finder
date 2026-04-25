from fastapi import FastAPI, APIRouter
import time
from datetime import datetime


from env_finder.api.models.stats import Health

app = FastAPI()
api = APIRouter(prefix="/api")


start_time_ms = time.time()
start_time_ts = datetime.fromtimestamp(start_time_ms).strftime('%Y-%m-%d %H:%M:%S')


@api.get("/health", response_model=Health)
def health():
    return Health(
        uptime_seconds = int(time.time() - start_time_ms),
        up_since_epoch_ms = start_time_ms,
        up_since_utc=start_time_ts
    )


@api.get("/stats/latest")
def stats():
    pass


@api.get("/stats/all")
def stats_all():
    pass



@api.get("/hits/all")
def hits():
    pass



@api.get("/secrets/all")
def credentials():
    pass



app.include_router(api)