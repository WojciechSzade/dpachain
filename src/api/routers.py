from fastapi import APIRouter
from src.api.admin.main import router as admin_router

router = APIRouter()

router.include_router(admin_router)