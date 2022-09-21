'''
File: scraping_plan.py
File Created: Wednesday, 21st September 2022 4:18:16 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from pydantic import BaseModel
from typing import List, Union, Optional
from beanie import PydanticObjectId
from pydantic import validator


class Scraping_planBase(BaseModel):
    title: str
    website: str
    plan: dict


class Scraping_plan_read(Scraping_planBase):
    owner_id:  PydanticObjectId


class Scraping_plan_write(Scraping_planBase):
    owner_id:  PydanticObjectId

    @validator('plan')
    def must_validate_schema(cls, plan):
        # just testing validator decorator will implement the schema validation here later
        if "description" not in plan:
            raise ValueError("Must contain a description buddy")
        return plan


class Scraping_plan_update(Scraping_planBase):
    __annotations__ = {k: Optional[v]
                       for k, v in Scraping_planBase.__annotations__.items()}

    @validator('plan')
    def must_validate_schema(cls, plan):
        # just testing validator decorator will implement the schema validation here later
        if "description" not in plan:
            raise ValueError("Must contain a description buddy")
        return plan
