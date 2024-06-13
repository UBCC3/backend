from fastapi import APIRouter, Depends, FastAPI, Response, status, Body, HTTPException
from fastapi.security import HTTPBearer
from ..database.user_management import (
    check_user_exists,
    add_new_user,
    get_all_users,
    update_user,
)

from ..models import UserModel, JwtErrorModel
from ..util import VerifyToken, token_auth
from typing import Union

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

token_auth_schema = HTTPBearer()


@router.get("/", response_model=Union[list[UserModel], JwtErrorModel])
async def get_users(response: Response, token: str = Depends(token_auth)):
    return get_all_users()


@router.get("/user-exists", response_model=Union[bool, JwtErrorModel])
async def get_user_exists(
    email: str, response: Response, token: str = Depends(token_auth)
):
    return check_user_exists(email)


@router.post("/", response_model=Union[bool, JwtErrorModel])
async def create_user(
    user: UserModel, response: Response, token: str = Depends(token_auth)
):
    user_exists = check_user_exists(user.email)
    if user_exists:
        raise HTTPException(status_code=400, detail="Email already registered")

    return add_new_user(user.email)


@router.patch("/", response_model=Union[bool, JwtErrorModel])
async def patch_user(
    user: UserModel, response: Response, token: str = Depends(token_auth)
):
    res = update_user(user)
    if not res:
        raise HTTPException(status_code=404, detail="User not found")
    else:
        return update_user(user)
