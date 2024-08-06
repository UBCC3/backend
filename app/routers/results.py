from fastapi import APIRouter, Depends, FastAPI, Response, status, Body, HTTPException
from fastapi.security import HTTPBearer
from ..database.calculation_management import (
    get_all_available_basis_sets,
    get_all_available_calculations,
    get_all_available_methods,
    get_all_available_solvent_effects
)

from ..models import (
    JwtErrorModel,
    CalculationOptionModel
)
from ..util import VerifyToken, token_auth
from typing import Union

router = APIRouter(
    prefix="/results",
    tags=["results"],
    responses={404: {"description": "Not found"}},
)

token_auth_schema = HTTPBearer()

@router.get("/job", response_model=Union[dict, JwtErrorModel])
async def get_job_result(
    job_id: str, request: Request, response: Response, token: str = Depends(token_auth)
):
    #TODO: Remove dummy value later
    return True