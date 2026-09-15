from fastapi import FastAPI, APIRouter


app = FastAPI()
api = APIRouter(prefix="/api")



@api.get("/health", status_code=204)
async def health(): ...



@api.get("/stats")
async def stats():
    pass


app.include_router(api)