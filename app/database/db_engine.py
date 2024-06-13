from sqlalchemy import Engine, create_engine, text
from pydantic import BaseModel, PrivateAttr

from .entity_names import DB_NAME
import logging
import os
from os.path import join, dirname
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = os.getcwd()+"/.env"
load_dotenv(dotenv_path)
class DB_Engine(BaseModel):
    _engine: Engine = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        host = os.environ.get("RDS_HOST")
        db_username= os.environ.get("RDS_USERNAME")
        db_passwd = os.environ.get("RDS_PASSWORD")

        db_url = f"postgresql://{db_username}:{db_passwd}@{host}/{DB_NAME}"
        self._engine = create_engine(db_url, echo=True)

    @property
    def engine(self) -> Engine:
        return self._engine

    def validate_connection(self):
        with self.engine.connect() as conn:
            result = conn.execute(text("select 'test'"))


handler = logging.FileHandler("/tmp/ubcc3-sql.log")
handler.setLevel(logging.DEBUG)
logger = logging.getLogger("sqlalchemy.engine")
logger.propagate = False
logger.addHandler(handler)

db_engine = DB_Engine()
