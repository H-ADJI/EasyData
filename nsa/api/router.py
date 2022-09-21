from nsa.api.routes import authentication, project
from fastapi import APIRouter

router = APIRouter()

router.include_router(authentication.router, prefix="/user",
                      tags=["Authentication"])
router.include_router(project.router, prefix="/project",
                      tags=["Authentication"])
