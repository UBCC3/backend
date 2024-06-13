from sqlalchemy import Table
from sqlalchemy.ext.declarative import declarative_base
from .entity_names import (
    USERS_TABLE_NAME,
    JOBS_TABLE_NAME,
    STRUCTURES_TABLE_NAME,
    STRUCTURE_PROPERTIES_TABLE_NAME,
    JOB_TAGS_TABLE_NAME,
    AVAILABLE_BASIS_SETS,
    AVAILABLE_CALCULATIONS,
    AVAILABLE_METHODS,
    AVAILABLE_SOLVENT_EFFECTS
)
from .db_engine import db_engine


Base = declarative_base()


class User(Base):
    __table__ = Table(USERS_TABLE_NAME, Base.metadata, autoload_with=db_engine.engine)


class Job(Base):
    __table__ = Table(JOBS_TABLE_NAME, Base.metadata, autoload_with=db_engine.engine)


class Structure(Base):
    __table__ = Table(STRUCTURES_TABLE_NAME, Base.metadata, autoload_with=db_engine.engine)


class Structure_Property(Base):
    __table__ = Table(
        STRUCTURE_PROPERTIES_TABLE_NAME, Base.metadata, autoload_with=db_engine.engine
    )


class Job_Tags(Base):
    __table__ = Table(
        JOB_TAGS_TABLE_NAME, Base.metadata, autoload_with=db_engine.engine
    )


class Available_Calculations(Base):
    __table__ = Table(
        AVAILABLE_CALCULATIONS, Base.metadata, autoload_with=db_engine.engine
    )


class Available_Basis_Sets(Base):
    __table__ = Table(
        AVAILABLE_BASIS_SETS, Base.metadata, autoload_with=db_engine.engine
    )


class Available_Methods(Base):
    __table__ = Table(AVAILABLE_METHODS, Base.metadata, autoload_with=db_engine.engine)

class Available_Solvent_Effects(Base):
    __table__ = Table(AVAILABLE_SOLVENT_EFFECTS, Base.metadata, autoload_with=db_engine.engine)