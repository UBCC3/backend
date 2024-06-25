import base64
import json
import os
import subprocess
from typing import Dict
from uuid import UUID

from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..database.db_engine import db_engine
from ..database.db_tables import Job
from ..database.job_management import update_job
from ..models import JobStatus, UpdateJobDTO
from ..util import create_presigned_post

dotenv_path = os.getcwd()+"/.env"
load_dotenv(dotenv_path)

def interaction_with_cluster():
    check_jobs_status()

def check_jobs_status():
    jobs_dict = get_all_running_jobs_as_dict()
    json_data = json.dumps(jobs_dict)

    ssh_command = ["ssh", "cluster", "python3 check_status.py"]

    try:
        process = subprocess.Popen(
            ssh_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=json_data)
        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=stderr)
        json_data = base64.b64decode(stdout).decode('utf-8')
        return_data = json.loads(json_data)
        for key, value in return_data.items():
            if value == 0:
                pass
            elif value == 1:
                fetch_result(key)
            else:
                error_message = value
                update_data = UpdateJobDTO(status=JobStatus.FAILED, parameters={"error_message": error_message})
                update_job(key, update_data)
    except subprocess.CalledProcessError as e:
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
    send_data = {"JobID": job_id, "PresignedResponse": response}
    json_data = json.dumps(send_data)
    encoded_json_data = base64.b64encode(json_data.encode()).decode('utf-8')

    ssh_command = ["ssh", "cluster", "python3 fetch_organized_result.py"]

    try:
        process = subprocess.Popen(
            ssh_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=encoded_json_data)
        if process.returncode != 0:
            raise HTTPException(status_code=500, detail=stderr)
        json_data = base64.b64decode(stdout).decode('utf-8')
        return_data = json.loads(json_data)

        #TODO: process the return_data

    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail="Failed to decode JSON from returned data.")

#TODO: add the function to send presigned URL for the zip file
