from .db_engine import db_engine

from .db_tables import Job, Structure
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import desc, func
from typing import List, Union


from typing import List
import sys
import subprocess
import uuid
from ..models import JobModel, JobStatus, CreateJobDTO, UpdateJobDTO, StructureOrigin
from fastapi import File, UploadFile

from ..util import upload_to_s3, item_to_dict


def get_all_jobs() -> List[JobModel]:
    """Gets all jobs

    Returns:
        List[JobModel]: Array of Jobs
    """
    with Session(db_engine.engine) as session:
        jobs = session.query(Job).all()

    return jobs


def get_all_running_jobs(email: str) -> List[JobModel]:
    """Gets all jobs that are running or submitted

    Args:
        email (str): email

    Returns:
        List[JobModel]: Array of Jobs
    """
    status_values = [JobStatus.RUNNING, JobStatus.SUBMITTED]

    with Session(db_engine.engine) as session:
        jobs = session.query(Job).filter(
            Job.userid == email, Job.status.in_(status_values)
        )

    return jobs

def get_all_completed_jobs(email: str) -> List[JobModel]:
    """Gets all the jobs that are not running or submitted

    Args:
        email (str): email

    Returns:
        List[JobModel]: Array of Jobs
    """
    status_values = [JobStatus.FAILED, JobStatus.CANCELLED, JobStatus.COMPLETED]

    with Session(db_engine.engine) as session:
        jobs = (
            session.query(Job)
            .filter(Job.userid == email, Job.status.in_(status_values))
            .all()
        )

    return jobs


def get_completed_jobs_count(email: str, filter: str) -> int:
    """Gets the count of jobs for a specific status

    Args:
        email (str): email
        filter (str): Status of jobs to get count for

    Returns:
        int: Number of jobs
    """
    if filter == "All":
        status_values = [JobStatus.FAILED, JobStatus.CANCELLED, JobStatus.COMPLETED]
    elif filter == "Completed":
        status_values = [JobStatus.COMPLETED]
    elif filter == "Failed":
        status_values = [JobStatus.FAILED, JobStatus.CANCELLED]
    elif filter == "Cancelled":
        status_values = [JobStatus.CANCELLED]

    with Session(db_engine.engine) as session:
        total_count = (
            session.query(Job)
            .filter(Job.userid == email, Job.status.in_(status_values))
            .count()
        )

    return total_count


def get_paginated_completed_jobs(
    email: str, limit: int, offset: int, filter: str
) -> List[Job]:
    """Gets the paginated data for completed jobs

    Args:
        email (str): email
        limit (int): How many entries to fetch 
        offset (int): Starting at which index
        filter (str): Job status

    Returns:
        List[Job]: Array of Jobs
    """
    if filter == "All":
        status_values = [JobStatus.FAILED, JobStatus.CANCELLED, JobStatus.COMPLETED]
    elif filter == "Completed":
        status_values = [JobStatus.COMPLETED]
    elif filter == "Failed":
        status_values = [JobStatus.FAILED]
    elif filter == "Cancelled":
        status_values = [JobStatus.CANCELLED]

    with Session(db_engine.engine) as session:
        jobs = (
            session.query(Job)
            .filter(Job.userid == email, Job.status.in_(status_values))
            .order_by(desc(Job.finished))
            .offset(offset)
            .limit(limit)
            .all()
        )

    return jobs


def post_new_job(
    email: str, job: CreateJobDTO, file: UploadFile = File(None)
) -> Union[JobModel, bool]:
    """Create new job entry

    Args:
        email (str): email
        job (CreateJobDTO): DTO of job
        file (UploadFile, optional): File of chemical structure. NOTE file might be required

    Returns:
        Union[JobModel, bool]: Returns a Job or false if fails
    """
    with Session(db_engine.engine) as session:
        try:
            # create new row in job table
            # TODO: ensure auth0 makes the email accessible.
            job = Job(
                id=uuid.uuid4(),
                userid=email,
                job_name=job.job_name,
                submitted= func.now(),
                parameters=job.parameters,
            )

            session.add(job)
            session.commit()
            # if source is upload, create new row in structure table
            if job.parameters["source"] == StructureOrigin.UPLOADED:
                structure = Structure(
                    id=uuid.uuid4(),
                    jobid=job.id,
                    userid=email,
                    name=job.job_name,
                    source=job.parameters["source"],
                )
                
                 # upload structure file to s3
                # s3 structure 
                upload_to_s3(file, structure.id)
            
                session.add(structure)
                session.commit()

            session.refresh(job)
            # TODO: change for deployment
            script_location = "cluster-api/submit_job.py"
            cluster_command = [
                "ssh","cluster","python3", script_location, job.parameters
            ]
            print("Parameters: ",job.parameters, "\n")
            return item_to_dict(job)
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error: {str(e)}")
            return False


def update_job(job_id: uuid.UUID, update_job_dto: UpdateJobDTO) -> bool:
    """Updates a job

    Args:
        job_id (uuid.UUID): Job ID
        update_job_dto (UpdateJobDTO): DTO to update

    Returns:
        bool: Returns True if successful update or False on fail
    """
    with Session(db_engine.engine) as session:
        try:
            job = session.query(Job).filter_by(id=job_id).first()

            if not job:
                return False

            job.started = update_job_dto.started
            job.finished = update_job_dto.finished
            job.status = update_job_dto.status

            session.commit()

            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error: {str(e)}")
            return False


def remove_job(job_id: uuid.UUID) -> bool:
    """Removes a Job from the Job Table

    Args:
        job_id (uuid.UUID): Job ID

    Returns:
        bool: Returns True if successful delete or False on fail
    """
    with Session(db_engine.engine) as session:
        try:
            job_record = session.get(Job, job_id)
            session.delete(job_record)
            session.flush()
            session.commit()

            return True
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error: {str(e)}")
            return False

