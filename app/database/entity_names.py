import os
from dotenv import load_dotenv

dotenv_path = os.getcwd()+"/.env"
load_dotenv(dotenv_path)

DB_NAME = os.environ.get("RDS_DBNAME")

JOB_TAGS_TABLE_NAME = "job_tags"
STRUCTURE_PROPERTIES_TABLE_NAME = "structure_properties"
STRUCTURES_TABLE_NAME = "structures"
JOBS_TABLE_NAME = "jobs"
USERS_TABLE_NAME = "users"
AVAILABLE_CALCULATIONS = "available_calculations"
AVAILABLE_BASIS_SETS = "available_basis_sets"
AVAILABLE_METHODS = "available_methods"
AVAILABLE_SOLVENT_EFFECTS = 'available_solvent_effects'
