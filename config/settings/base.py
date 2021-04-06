# -*- coding: utf-8 -*-
from pydantic import BaseSettings
import dotenv

class APIBaseSettings(BaseSettings):
    DB_NAME: str
