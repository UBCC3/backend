from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Any, Dict, List
from uuid import UUID

from enum import Enum
from fastapi import Form


class UserModel(BaseModel):
    email: EmailStr
    created: Optional[datetime] = None
    lastlogin: Optional[datetime] = None
    active: Optional[bool] = None
    admin: Optional[bool] = None


class JwtErrorModel(BaseModel):
    status: str
    msg: str
    
class CalculationOptionModel(BaseModel):
    id: int
    name: str

class JobStatus(str, Enum):
    SUBMITTED = "SUBMITTED"
    RUNNING = "RUNNING"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class JobModel(BaseModel):
    id: UUID
    created: datetime
    userid: EmailStr
    job_name: str
    submitted: Optional[datetime] = None
    started: Optional[datetime] = None
    finished: Optional[datetime] = None
    status: Optional[JobStatus] = JobStatus.SUBMITTED
    parameters: Optional[Dict[str, Any]] = None


class PaginatedJobModel(BaseModel):
    offset: int
    limit: int
    total_count: int
    filter: str
    data: List[JobModel]


class CreateJobDTO(BaseModel):
    job_name: str
    parameters: Optional[Dict[str, Any]] = None


class UpdateJobDTO(BaseModel):
    started: Optional[datetime] = None
    finished: Optional[datetime] = None
    status: Optional[JobStatus] = JobStatus.SUBMITTED
    parameters: Optional[Dict[str, Any]] = None


class StructureOrigin(str, Enum):
    UPLOADED = "UPLOADED"
    CALCULATED = "CALCULATED"


class StructureModel(BaseModel):
    id: UUID
    source: StructureOrigin
    name: str
    jobid: UUID
    created: datetime
    userid: EmailStr
