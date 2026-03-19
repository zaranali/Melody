import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from config import PORT

log = logging.getLogger(__name__)

_server: uvicorn.Server | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    log.info(f"Web service started on port {PORT}")
    yield
    log.info("Web service shutting down")


web_app = FastAPI(
    title="Melody Bot",
    description="Status API for Melody Music Bot",
    version="1.0.0",
    lifespan=lifespan
)


@web_app.get("/", summary="Health Check")
async def root():
    """Returns the bot's operational status."""
    return JSONResponse({"status": "ok", "message": "Bot is running!"})


@web_app.get("/ping", summary="Ping")
async def ping():
    return JSONResponse({"ping": "pong"})


async def start_web_server():
    """Start FastAPI server non-blocking on the current event loop."""
    global _server
    try:
        config = uvicorn.Config(
            app=web_app,
            host="0.0.0.0",
            port=PORT,
            log_level="error",
            loop="none"   # use the existing asyncio event loop
        )
        _server = uvicorn.Server(config)
        # serve() blocks, so run it as a background task
        asyncio.create_task(_server.serve())
        log.info(f"FastAPI web service starting on port {PORT}")
    except Exception as e:
        log.error(f"Failed to start web service: {e}")
