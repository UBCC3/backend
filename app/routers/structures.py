from fastapi import APIRouter, Depends, Response 
from fastapi.security import HTTPBearer
from ..database.structure_management import(
    get_all_structure
)

from ..models import JwtErrorModel, StructureModel
from ..util import token_auth
from typing import Union

router = APIRouter(
    prefix="/structures",
    tags=["structures"],
    responses={404: {"description": "Not found"}},
)

token_auth_schema = HTTPBearer()


@router.get("/", response_model=Union[list[StructureModel], JwtErrorModel])
async def get_structures(response: Response, token: str = Depends(token_auth)):
    return get_all_structure()
