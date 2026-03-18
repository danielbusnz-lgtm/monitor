import time
from contextlib import asynccontextmanager
from fastapi import FastAPI
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


@app.get("/status")
def status():
    now = time.time()
    services = db.get_all_services()
    result = []
    for s in services:
        last = s["last_ping"]
        if last is None:
            state = "unknown"
            ago = None
        else:
            elapsed = now - last
            grace = s["interval_seconds"] * 1.5
            state = "down" if elapsed > grace else "up"
            ago = int(elapsed)
        result.append({"name": s["name"], "status": state, "last_ping_seconds_ago": ago})
    return result
