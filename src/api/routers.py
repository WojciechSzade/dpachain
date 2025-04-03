from fastapi import APIRouter
from src.api.admin import router as admin_router
from src.api.staff import router as staff_router
from src.api.user import router as user_router


router = APIRouter()

router.include_router(admin_router)
router.include_router(staff_router)
router.include_router(user_router)
