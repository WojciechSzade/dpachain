from fastapi import APIRouter
from src.api.admin.main import router as admin_router
from src.api.main import router as main_router

router = APIRouter()

router.include_router(main_router)
router.include_router(admin_router)