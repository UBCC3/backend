from .db_engine import db_engine

from .db_tables import Available_Basis_Sets, Available_Calculations, Available_Methods, Available_Solvent_Effects
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import asc

from typing import List
from ..models import (
    CalculationOptionModel
)


def get_all_available_calculations() -> List[CalculationOptionModel]:
    with Session(db_engine.engine) as session:
        available_calculations = (
            session.query(Available_Calculations)
            .order_by(asc(Available_Calculations.id))
            .all()
        )

    return available_calculations


def get_all_available_basis_sets() -> List[CalculationOptionModel]:
    with Session(db_engine.engine) as session:
        available_basis_sets = (
            session.query(Available_Basis_Sets)
            .order_by(asc(Available_Basis_Sets.id))
            .all()
        )

    return available_basis_sets


def get_all_available_methods() -> List[CalculationOptionModel]:
    with Session(db_engine.engine) as session:
        available_methods = (
            session.query(Available_Methods).order_by(asc(Available_Methods.id)).all()
        )

    return available_methods

def get_all_available_solvent_effects() -> List[CalculationOptionModel]:
    with Session(db_engine.engine) as session:
        available_solvent_effects = (
            session.query(Available_Solvent_Effects).order_by(asc(Available_Solvent_Effects.id)).all()
        )
        
    return available_solvent_effects