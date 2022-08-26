# -*- coding: utf-8 -*-
from .local import LocalSettings


class TestingSettings(LocalSettings):

    class Config:
        env_file = 'tests/.env.test'
        env_file_encoding = 'utf-8'

    def __init__(self):
        super(TestingSettings, self).__init__()

settings = TestingSettings()
