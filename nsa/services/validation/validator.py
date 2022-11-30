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


def json_data_validator(path_to_schema):
    with open(path_to_schema, "r") as f:
        schema: dict = json.load(f)
        validator = fastjsonschema.compile(schema)
    return validator


scraping_plan_validator = json_data_validator(
    path_to_schema=PATH_SCRAPING_PLAN_SCHEMA)


