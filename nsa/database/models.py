'''
File: models.py
File Created: Tuesday, 20th September 2022 10:31:58 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from datetime import datetime
from fastapi_users.db import BeanieBaseUser
from beanie import Document, PydanticObjectId, Link
from typing import List, Optional


class User(BeanieBaseUser[PydanticObjectId]):
    first_name: str
    last_name: str

class Project(Document):
    description: str
    title: str
    tags: Optional[List[str]]
    image: Optional[str]
    # TODO: fix athentication and add owner link
    # owner: Link[User]
    # jobs: Optional[List[Link[Scraping_job]]]

    class Settings:
        name = "projects"
