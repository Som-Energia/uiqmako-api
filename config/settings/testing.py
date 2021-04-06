# -*- coding: utf-8 -*-
from pydantic import BaseSettings
from .base import APIBaseSettings
import dotenv

class TestingSettings(APIBaseSettings):
    class Config:
        env_file = 'tests/.env.test'
        env_file_encoding = 'utf-8'

    def __init__(self):
        super(TestingSettings, self).__init__()

settings = TestingSettings()
