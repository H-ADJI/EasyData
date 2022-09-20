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
from typing import List
from nsa.models.project import Frequency


class User(BeanieBaseUser[PydanticObjectId]):
    first_name: str
    last_name: str


class Project(Document):
    description: str
    title: str
    tags: List[str]
    image: str
    owner: User

    class Settings:
        name = "projects"


class Scraping_plan(Document):
    title: str
    description: str
    website: List[str]

    class Settings:
        name = "scraping_plans"


class Scraping_job(Document):
    description: str
    title: str
    schedule_date: datetime
    frequency: Frequency
    scraping_plan: Scraping_plan

    class Settings:
        name = "scraping_jobs"


class Output_data(Document):
    data: dict

    class Settings:
        name = "data_nd_analytics"
