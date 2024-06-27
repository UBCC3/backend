from typing import Dict
from uuid import UUID

import asyncio
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
    jobs_dict = process_running_jobs()
    try:
        return_data = cluster_call("check", jobs_dict)
        for job_id, details in return_data.items():
            if details == 0:
                pass
            elif details['state'] == "COMPLETED":
                update_data = UpdateJobDTO(
                    started=details['start_time'], 
                    finished=details['end_time']
                ) 
                update_job(job_id, update_data)
                upload_results(job_id)
            else:
                error_message = f'state {details['state']} with exit code {details['exitcode']} and reason {details['reason']}'
                update_data = UpdateJobDTO(
                    status=JobStatus.FAILED, 
                    started=details['start_time'], 
                    finished=details['end_time'], 
                    error_message=error_message
                )
                update_job(job_id, update_data)
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
            jobs_dict[job.id] = 0

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

def clean_results(job_id):
    parameters = {"JobID": job_id}
    return_data = cluster_call("clean", parameters)
    