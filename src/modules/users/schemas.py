from beanie import PydanticObjectId

from src.pydantic_base import BaseSchema


class CreateUser(BaseSchema):
    innohassle_id: str


class ViewUser(BaseSchema):
    id: PydanticObjectId
    innohassle_id: str


class UserAuthData(BaseSchema):
    user_id: PydanticObjectId
    innohassle_id: str
