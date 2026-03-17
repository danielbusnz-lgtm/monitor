import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import db
import checker


@asynccontextmanager
async def lifespan(app):
    checker.start_checker()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/ping/{service_name}")
def ping(service_name: str, interval: int = 3600):
    db.record_ping(service_name, interval)
    return {"ok": True}
