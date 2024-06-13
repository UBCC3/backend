from .db_engine import db_engine

from .db_tables import Structure
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

import uuid
from ..models import StructureModel, StructureOrigin
from typing import List


def post_structure(
    job_id: uuid.uuid4,
    user_id: str,
    structure_name: str,
    structure_origin: StructureOrigin,
) -> bool:
    """Create new Structure entry

    Args:
        job_id (uuid.uuid4): Job ID
        user_id (str): User ID
        structure_name (str): Structure name
        structure_origin (StructureOrigin): Upload or Calculated

    Returns:
        bool: Returns True if successful or False on fail
    """
    with Session(db_engine.engine) as session:
        try:
            structure = Structure(
                id=uuid.uuid4(),
                jobid=job_id,
                userid=user_id,
                name=structure_name,
                source=structure_origin,
            )
            session.add(structure)
            session.commit()
            return True
        except SQLAlchemyError as e:
            print("error")
            session.rollback()
            print(f"Error: {str(e)}")
            return False


def get_structure_by_job_id(job_id: uuid.uuid4) -> StructureModel:
    """Gets a structure from Job ID

    Args:
        job_id (uuid.uuid4): Job ID

    Returns:
        StructureModel: Structure
    """
    with Session(db_engine.engine) as session:
        structure = session.query(Structure).filter_by(jobid=job_id).first()
    return structure


def get_all_structure() -> list[StructureModel]:
    """Gets all structures

    Returns:
        list[StructureModel]: Array of structures
    """
    with Session(db_engine.engine) as session:
        structures = session.query(Structure).all()

    return structures