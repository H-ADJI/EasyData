from nsa.api.routes import authentication, project, scraping_plan, scheduling
from fastapi import APIRouter

router = APIRouter(prefix="/api")

router.include_router(authentication.router, prefix="/user",
                      tags=["Authentication"])
router.include_router(project.router, prefix="/project",
                      tags=["Projects"])
router.include_router(scraping_plan.router, prefix="/plan",
                      tags=["Plans"])
router.include_router(scheduling.router, prefix="/job",
                      tags=["Scraping Jobs"])
