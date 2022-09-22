'''
File: validator.py
File Created: Thursday, 22nd September 2022 9:45:52 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''

import fastjsonschema
from nsa.constants.constants import PATH_SCRAPING_PLAN_SCHEMA
import json


class Scraping_plan_validator(object):
    schema_file_path = PATH_SCRAPING_PLAN_SCHEMA

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Scraping_plan_validator, cls).__new__(cls)
            with open(cls.schema_file_path, "r") as f:
                schema: dict = json.load(f)
                validator = fastjsonschema.compile(schema)
            cls.validator = validator
        return cls.instance
