'''
File: project.py
File Created: Monday, 19th September 2022 5:00:22 pm
Author: KHALIL HADJI 
-----
Copyright:  H-adji 2022
'''
from pydantic import BaseModel
from typing import List, Optional
from beanie import PydanticObjectId


class ProjectBase(BaseModel):
    description: str
    title: str
    url: str
    tags: List[str]
    image: str


class Project_read(ProjectBase):
    owner_id: PydanticObjectId
    id: Optional[PydanticObjectId]


class Project_update(ProjectBase):
    __annotations__ = {k: Optional[v]
                       for k, v in ProjectBase.__annotations__.items()}
