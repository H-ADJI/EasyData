from nsa.api.routes import authentication
from fastapi import APIRouter

router = APIRouter()

router.include_router(authentication.router, prefix="/user",
                      tags=["Authentication"])
