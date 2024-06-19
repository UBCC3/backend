import sys
import subprocess
import os
from dotenv import load_dotenv
from pathlib import Path

from ..models import CreateJobDTO
env_var = os.getcws()+"/.env"
load_dotenv(env_var)

def submit_job(job: CreateJobDTO) -> bool:
    """
    Submit a new job to the cluster using ssh
    
    Args:
    job: DTO of job

    Returns: 
    
    A boolean value for if the job was submitted
    """
    # TODO: change for deployment
    script_loc = os.environ.get("CLUSTER_LOC")
    cluster_command = [
        "ssh","cluster","python3", script_loc
    ]
    try:
        submit_process = subprocess.Popen(cluster_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = subprocess.communicate(job.parameters)
    except subprocess.CalledProcessError as err:
        print("ERROR in calling cluster {err.stderr}")
        return False
    else:
        return True
    
def cancel_job(job_id) -> bool:
    """
    Cancel a job currently queued or running.

    Args:
    job_id: str provided as job id by SQL

    Returns: A boolean value for if it failed or succeeded
    """
    # TODO: change for development
    # NOTE: adjust the .env file
    script_loc = os.environ.get("CLUSTER_LOC")
    ssh_command = [
        "ssh", "cluster", "python3", script_loc
    ]

    try:
        submit_process = subprocess.Popen(ssh_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = subprocess.communicate(job_id)
    except subprocess.CalledProcessError as err:
        print("ERROR in calling cluster {err.stderr}")
        return False
    else:
        return True