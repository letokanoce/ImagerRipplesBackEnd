from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.router.insight import router as insights_router
from app.settings import *

app = FastAPI()
app.add_middleware(CORSMiddleware,
                   allow_credentials=True,
                   allow_origins=["*"],
                   allow_methods=["*"],
                   allow_headers=["*"])


@app.on_event("startup")
async def start_event():
    return mongodb_client, oss2_bucket, redis_client


@app.on_event("shutdown")
async def shutdown_event():
    mongodb_client.close_connection()
    oss2_bucket.close_connection()
    redis_client.close_connection()


@app.get("/")
async def read_root():
    return {"HELLO": "Image Ripples"}


app.include_router(insights_router)
