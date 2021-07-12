# -*- coding: utf-8 -*-
import os
from importlib import import_module
ENVIRONMENT_VARIABLE = 'UIQMAKO_MODULE_SETTINGS'

os.environ.setdefault('UIQMAKO_MODULE_SETTINGS', 'config.settings.local')

mod = import_module(os.getenv(ENVIRONMENT_VARIABLE))
settings = mod.settings
