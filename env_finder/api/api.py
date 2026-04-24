from fastapi import FastAPI, APIRouter

app = FastAPI()
api = APIRouter(prefix="/api")


@api.get("/stats")
def stats():
    """
    uptime: ...
    """
    pass


@api.get("/stats/all")
def stats_all():
    pass



@api.get("/hits")
def hits():
    pass



@api.get("/credentials")
def credentials():
    pass



app.include_router(api)