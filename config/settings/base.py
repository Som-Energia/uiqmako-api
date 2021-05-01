# -*- coding: utf-8 -*-
from pydantic import BaseSettings
import dotenv

class APIBaseSettings(BaseSettings):
    DB_NAME: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    ALGORITHM: str
    SECRET_KEY: str
    TEMPLATE_REPO_PATH: str
