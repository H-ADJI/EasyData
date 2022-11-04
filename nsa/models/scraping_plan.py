'''
File: scraping_plan.py
File Created: Wednesday, 21st September 2022 4:18:16 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from pydantic import BaseModel
from typing import Optional
from beanie import PydanticObjectId
from pydantic import validator
from nsa.validation.validator import fastjsonschema
from nsa.constants.constants import PATH_SCRAPING_PLAN_SCHEMA
import json


class Scraping_planBase(BaseModel):
    title: str
    website: str
    plan: dict


class Scraping_plan_read(Scraping_planBase):
    owner_id:  PydanticObjectId


class Scraping_plan_write(Scraping_planBase):

    @validator('plan')
    def must_validate_schema(cls, plan):
        # TODO: fix the validator class have some weird behaviour
        # schema_validator = Scraping_plan_validator()
        # schema_validator.validator(plan)
        # The following approach is temporary ( lots of overhead loading  and compiling schema each time)
        with open(PATH_SCRAPING_PLAN_SCHEMA, "r") as f:
            schema: dict = json.load(f)
            fastjsonschema.validate(definition=schema, data=plan)
        return plan


class Scraping_plan_update(Scraping_planBase):
    __annotations__ = {k: Optional[v]
                       for k, v in Scraping_planBase.__annotations__.items()}

    @validator('plan')
    def must_validate_schema(cls, plan):
        # TODO: fix the validator class have some weird behaviour
        # schema_validator = Scraping_plan_validator()
        # schema_validator.validator(plan)
        # The following approach is temporary ( lots of overhead loading  and compiling schema each time)
        with open(PATH_SCRAPING_PLAN_SCHEMA, "r") as f:
            schema: dict = json.load(f)
            fastjsonschema.validate(definition=schema, data=plan)
        return plan
