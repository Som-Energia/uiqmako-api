# -*- coding: utf-8 -*-
from .base import APIBaseSettings

class LocalSettings(APIBaseSettings):

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

    def __init__(self):
        super(LocalSettings, self).__init__()


settings = LocalSettings()
