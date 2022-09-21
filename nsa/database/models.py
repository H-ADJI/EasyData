'''
File: models.py
File Created: Tuesday, 20th September 2022 10:31:58 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from datetime import datetime
from fastapi_users.db import BeanieBaseUser
from beanie import Document, PydanticObjectId
from typing import List, Optional


class User(BeanieBaseUser[PydanticObjectId]):
    first_name: str
    last_name: str


class Project(Document):
    description: str
    title: str
    tags: Optional[List[str]]
    image: Optional[str]
    owner_id:  PydanticObjectId

    class Settings:
        name = "projects"


class Scraping_plan(Document):
    owner_id:  PydanticObjectId
    website: str
    title: str
    plan: dict

    class Settings:
        name = "scraping_plans"
