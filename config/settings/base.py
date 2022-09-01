# -*- coding: utf-8 -*-
from pydantic import BaseSettings, BaseModel
from typing import Dict
import dotenv

class DatabaseConnectionData(BaseModel):
    NAME: str
    HOST: str
    PORT: int
    USER: str
    PWD: str

class ConnectionData(BaseModel):
    DB_NAME: str
    URI: str
    PORT: int
    USER: str
    PWD: str

class APIBaseSettings(BaseSettings):
    DB_CONFIG: DatabaseConnectionData
    ERP_CONNECTIONS: Dict[str, ConnectionData] = None
    ACCESS_TOKEN_EXPIRE_HOURS: int
    ALGORITHM: str
    SECRET_KEY: str
    TEMPLATE_REPO_PATH: str

    def erp_conn(self, _name):
        if not _name:
            _name = 'PROD'

        erp_conn = {
            'db': self.ERP_CONNECTIONS[_name].DB_NAME,
            'server': '{}:{}'.format(self.ERP_CONNECTIONS[_name].URI, self.ERP_CONNECTIONS[_name].PORT),
            'user': self.ERP_CONNECTIONS[_name].USER,
            'password': self.ERP_CONNECTIONS[_name].PWD
        }
        return erp_conn

