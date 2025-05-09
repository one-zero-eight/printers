from fastapi import APIRouter

from src.api.dependencies import USER_AUTH

router = APIRouter(prefix="/users", tags=["User"])


@router.get("/my_id", responses={401: {"description": "Unable to verify credentials OR Credentials not provided"}})
def get_current_user_id(innohassle_user_id: USER_AUTH) -> str:
    return innohassle_user_id
