# pyapi/web/api/monitoring.py - 監控相關端點
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check() -> None:
    """
    Checks the health of a project.

    It returns 200 if the project is healthy.
    """