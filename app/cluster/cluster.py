from typing import Dict
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..database.db_engine import db_engine
from ..database.db_tables import Job
from ..database.job_management import update_job
from ..models import JobStatus, UpdateJobDTO
from ..util import cluster_call, create_presigned_post

def interaction_with_cluster():
    check_jobs_status()

def check_jobs_status():
    jobs_dict = get_all_running_jobs_as_dict()
    try:
        return_data = cluster_call("check", jobs_dict)
        for key, value in return_data.items():
            if value == 0:
                pass
            elif value == 1:
                fetch_result(key)
            else:
                error_message = value
                update_data = UpdateJobDTO(status=JobStatus.FAILED, parameters={"error_message": error_message})
                update_job(key, update_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        

def get_all_running_jobs_as_dict() -> Dict[UUID, int]:
    status_values = [JobStatus.RUNNING, JobStatus.SUBMITTED]
    jobs_dict = {}

    with Session(db_engine.engine) as session:
        jobs = session.query(Job).filter(
            Job.status.in_(status_values)
        )
        for job in jobs:
            jobs_dict[job.id] = 0

    return jobs_dict

def fetch_result(job_id):
    object_name = f'/jobs/{job_id}/' # TODO: use the corerct path
    response = create_presigned_post(object_name)
    parameters = {"JobID": job_id, "PresignedResponse": response}
    try:
        return_data = cluster_call("fetch", parameters)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def submit_job(job):
    try:
        return_data = cluster_call("submit", job.parameters)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    else:
        if return_data["status"] == "SUCCESS":
            pass 
    
def cancel_job(job):
    try:
        return_data = cluster_call("cancel",job)
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))
    else:
        if return_data["status"] == "SUCCESS":
            pass 