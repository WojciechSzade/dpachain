from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.core.db import init_db
from src.core.models import Blockchain
from src.core.config import settings
from src.api.routers import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    client = init_db()
    app.state.blockchain = Blockchain(client)
    yield

app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
)

def get_blockchain():
    return app.state.blockchain

app.include_router(router)
