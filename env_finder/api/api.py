from fastapi import FastAPI, APIRouter


app = FastAPI()
api = APIRouter(prefix="/api")



@api.get("/health", status_code=200)
def health():
    return "API is healthy"



@api.get("/stats")
def stats():
    pass


app.include_router(api)