# -*- coding: utf-8 -*-
from pydantic import BaseSettings
from .base import APIBaseSettings
from typing import Dict, Any
import dotenv

class LocalSettings(APIBaseSettings):

    ERP_DB_NAME : str
    ERP_URI: str
    ERP_PORT: int
    ERP_USER: str
    ERP_PWD: str
    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

    def __init__(self):
        super(LocalSettings, self).__init__()

    def erp_conn(self):
        erp_conn = {
            'db': self.ERP_DB_NAME,
            'server': '{}:{}'.format(self.ERP_URI, self.ERP_PORT),
            'user': self.ERP_USER,
            'password': self.ERP_PWD
        }
        return erp_conn

settings = LocalSettings()