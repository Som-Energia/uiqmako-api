# -*- coding: utf-8 -*-
from pydantic import BaseSettings, BaseModel
import dotenv

class DatabaseConnectionData(BaseModel):
    NAME: str
    HOST: str
    PORT: int
    USER: str
    PWD: str

class APIBaseSettings(BaseSettings):
    DB_CONFIG: DatabaseConnectionData
    ACCESS_TOKEN_EXPIRE_HOURS: int
    ALGORITHM: str
    SECRET_KEY: str
    TEMPLATE_REPO_PATH: str