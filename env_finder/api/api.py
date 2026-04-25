from fastapi import FastAPI, APIRouter

app = FastAPI()
api = APIRouter(prefix="/api")


@api.get("/health")
def health():
    pass


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