from typing import Dict
from uuid import UUID

import asyncio
from datetime import datetime
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..database.db_engine import db_engine
from ..database.db_tables import Job
from ..database.job_management import update_job
from ..models import JobStatus, UpdateJobDTO
from ..util import cluster_call, create_presigned_post

def interaction_with_cluster():
    check_jobs_status()

def check_jobs_status():
    jobs_dict = process_running_jobs()
    parameters = {"jobs_dict": jobs_dict}
    try:
        return_data = cluster_call("check", parameters)
        for job_id, details in return_data.items():
            if details != 0:
                update_data = UpdateJobDTO(
                    status = JobStatus[details["status"]] if "status" in details else None,
                    started = datetime.fromisoformat(details["started"]) if "started" in details else None,
                    finished = datetime.fromisoformat(details["finished"]) if "finished" in details else None,
                    error_message = details["error_message"] if "error_message" in details else None,
                )
                update_job(job_id, update_data)
                if details["status"] == "COMPLETED" or "FAILED":
                    upload_results(job_id)            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def process_running_jobs() -> Dict[UUID, int]:
    status_values = [JobStatus.RUNNING, JobStatus.SUBMITTED]
    jobs_dict = {}

    with Session(db_engine.engine) as session:
        jobs = session.query(Job).filter(
            Job.status.in_(status_values)
        )
        for job in jobs:
            jobs_dict[job.id] = job.status

    return jobs_dict

async def upload_results(job_id):
    results = await asyncio.gather(
        upload_result(job_id, "archive"),
        upload_result(job_id, "jobs")
    )
    if all(status == 204 for status in results):
        clean_results(job_id)   
    else:
        raise HTTPException(status_code=207, detail="One or more uploads did not complete successfully")
    
async def upload_result(job_id, path_name):
    object_name = f'/{path_name}/{job_id}/' 
    response = create_presigned_post(object_name)
    type_value = "zip" if path_name == "archive" else "json"
    parameters = {"Type": type_value, "JobID": job_id, "PresignedResponse": response}
    try:
        return_data = await cluster_call("upload", parameters)
        return return_data["status_code"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def submit_job(job):
    try:
        return_data = cluster_call("submit", job)
    except Exception as error:
        return False
        # raise HTTPException(status_code=500, detail=str(error))
    else:
        if return_data["status"] == "SUCCESS":
            return True
            # return JSONResponse(content=return_data, status_code=200) 
        return False
def cancel_job(job):
    try:
        return_data = cluster_call("cancel",job)
    except Exception as error:
        return False
        # raise HTTPException(status_code=500, detail=str(error))
    else:
        if return_data["status"] == "SUCCESS":
            return True
            # return JSONResponse(content=return_data, status_code=200)
        return False
def clean_results(job_id):
    parameters = {"JobID": job_id}
    return_data = cluster_call("clean", parameters)
    