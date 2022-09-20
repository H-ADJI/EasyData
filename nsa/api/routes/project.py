'''
File: project.py
File Created: Tuesday, 20th September 2022 11:54:51 am
Author: KHALIL HADJI 
-----
Copyright:  HENCEFORTH 2022
'''
from fastapi import Depends, APIRouter, status
from .authentication import current_user
from nsa.models.project import ProjectIn
from nsa.database.models import Project
router = APIRouter()

# TODO: fix protected route bug
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(project: ProjectIn):
    new_project: Project = Project(**project.dict())
    print(new_project.dict())
    await new_project.insert()
    return new_project.dict()

# @router.get("/test", status_code=status.HTTP_201_CREATED)
# async def test(current_user=Depends(current_user)):
#     return "hello"


@router.get("", status_code=status.HTTP_201_CREATED)
async def get_all_projects():
    all_projects = Project.find_all()
    all_projects_list = await all_projects.to_list()
    return all_projects_list


@router.get("/{id}", status_code=status.HTTP_201_CREATED)
async def get_one_projects(id: str):
    project = await Project.get(document_id=id)
    return project


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def get_one_projects(id: str):
    project = await Project.get(document_id=id)
    await project.delete()
    return f"deleted {id}"


@router.patch("", status_code=status.HTTP_201_CREATED)
async def get_all_projects():
    all_projects = Project.find_all()
    all_projects_list = await all_projects.to_list()
    return all_projects_list
