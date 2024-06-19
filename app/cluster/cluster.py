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
    script_location = os.environ.get("CLUSTER_LOC")
    cluster_command = [
        "ssh","cluster","python3", script_location
    ]
    try:
        submit_process = subprocess.Popen(cluster_command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = subprocess.communicate(job.parameters)
    except subprocess.CalledProcessError as err:
        print("ERROR in calling cluster {err.stderr}")
        return False
    else:
        return True