from fastapi import FastAPI
from src.core.db import init_db
from src.core.config import settings



app = FastAPI(
    title=settings.PROJECT_NAME,
)

@app.on_event("startup")
async def startup_event():
    app.db = init_db()