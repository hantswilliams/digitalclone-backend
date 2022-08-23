from fastapi import APIRouter
from src.endpoints import start_task, check_task

router = APIRouter()
router.include_router(start_task.router)
router.include_router(check_task.router)
