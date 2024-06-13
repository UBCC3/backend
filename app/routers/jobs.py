from fastapi import (
    APIRouter,
    Depends,
    Response,
    Body,
    HTTPException,
    File,
    UploadFile,
    Form,
)
from fastapi.security import HTTPBearer
from ..database.job_management import (
    get_all_jobs,
    get_all_running_jobs,
    get_all_completed_jobs,
    get_paginated_completed_jobs,
    get_completed_jobs_count,
    post_new_job,
    update_job,
    remove_job,
)
from ..database.structure_management import get_structure_by_job_id

import json

from ..models import (
    JobModel,
    JwtErrorModel,
    PaginatedJobModel,
    CreateJobDTO,
    UpdateJobDTO
)
from ..util import token_auth, download_from_s3, read_from_s3
from typing import Union, Any
from uuid import UUID

router = APIRouter(
    prefix="/jobs",
    tags=["jobs"],
    responses={404: {"description": "Not found"}},
)

token_auth_schema = HTTPBearer()


@router.get("/", response_model=Union[list[JobModel], JwtErrorModel])
async def get_jobs(response: Response, token: str = Depends(token_auth)):
    jobs = get_all_jobs()

    job_dicts = [job.__dict__ for job in jobs]

    return job_dicts


@router.get("/in-progress", response_model=Union[list[JobModel], JwtErrorModel])
async def get_in_progress_jobs(
    email: str, response: Response, token: str = Depends(token_auth)
):
    jobs = get_all_running_jobs(email)

    job_dicts = [job.__dict__ for job in jobs]

    return job_dicts


@router.get("/all-completed", response_model=Union[list[JobModel], JwtErrorModel])
async def get_complete_jobs(
    email: str,
    response: Response,
    token: str = Depends(token_auth),
):
    jobs = get_all_completed_jobs(email)

    job_dicts = [job.__dict__ for job in jobs]

    return job_dicts


@router.get("/completed", response_model=Union[PaginatedJobModel, JwtErrorModel])
async def get_paginated_complete_jobs(
    email: str,
    response: Response,
    filter: str,
    limit: int = 5,
    offset: int = 0,
    token: str = Depends(token_auth),
):
    total_count = get_completed_jobs_count(email, filter)
    data = get_paginated_completed_jobs(email, limit, offset, filter)
    return {
        "offset": offset,
        "limit": limit,
        "total_count": total_count,
        "filter": filter,
        "data": data,
    }


@router.post("/", response_model=Union[JobModel, JwtErrorModel])
async def create_new_job(
    email: str = Form(...),
    job_name: str = Form(...),
    parameters: str = Form(...),
    file: UploadFile = File(None),
    token: str = Depends(token_auth),
):
    job = CreateJobDTO(job_name=job_name, parameters=json.loads(parameters))
    return post_new_job(email, job, file)


@router.patch("/{job_id}", response_model=Union[bool, JwtErrorModel])
async def patch_job(job_id: UUID, job: UpdateJobDTO, token: str = Depends(token_auth)):
    res = update_job(job_id, job)

    if not res:
        raise HTTPException(status_code=404, detail="Job not found")
    else:
        return True


@router.delete("/{job_id}", response_model=Union[bool, JwtErrorModel])
async def delete_job(job_id: UUID, token: str = Depends(token_auth)):
    return remove_job(job_id)


# NOTE: disabled for now
# @router.get("/download/{job_id}/{file_name}", response_model=Union[str, JwtErrorModel])
# async def download(
#     file_name: str,
#     job_id: UUID,
#     response: Response,
#     token: str = Depends(token_auth)
# ):
#     structure = get_structure_by_job_id(job_id)

#     return download_from_s3(file_name, structure.id)

# NOTE: disabled for now
# TODO: response type
# @router.get("/read-file/{job_id}/{file_name}", response_model=Union[Any, JwtErrorModel])
# async def read_file(
#     file_name: str,
#     job_id: UUID,
#     response: Response,
#     token: str = Depends(token_auth)
# ):
#     return read_from_s3(file_name, job_id)
