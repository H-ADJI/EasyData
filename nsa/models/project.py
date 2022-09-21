'''
File: project.py
File Created: Monday, 19th September 2022 5:00:22 pm
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from datetime import datetime
from pydantic import BaseModel
from typing import List, Union, Optional

class ProjectBase(BaseModel):
    description: str
    title: str
    tags: List[str]
    image: str


class Project_read(ProjectBase):
    pass


class Project_update(ProjectBase):
    __annotations__ = {k: Optional[v]
                       for k, v in ProjectBase.__annotations__.items()}
