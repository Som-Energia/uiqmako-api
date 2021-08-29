# -*- coding: utf-8 -*-
from pydantic import BaseModel
from .base import APIBaseSettings
from typing import Dict

class ConnectionData(BaseModel):
    DB_NAME: str
    URI: str
    PORT: int
    USER: str
    PWD: str


class LocalSettings(APIBaseSettings):
    ERP_CONNECTIONS: Dict[str, ConnectionData] = None

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

    def __init__(self):
        super(LocalSettings, self).__init__()

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


settings = LocalSettings()