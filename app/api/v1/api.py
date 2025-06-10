from fastapi import APIRouter

from .endpoints import achivement, auth, character, city, event, file, healthcheck, occupation, tasuki, user, nfc # Added nfc

api_router = APIRouter()

# Include the healthcheck router
api_router.include_router(
    healthcheck.router,
    prefix="/healthcheck",
    tags=["healthcheck"]
)

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(tasuki.router, prefix="/tasuki", tags=["tasuki"])
api_router.include_router(file.router, prefix="/files", tags=["files"])
api_router.include_router(city.router, prefix="/cities", tags=["cities"])
api_router.include_router(occupation.router, prefix="/occupations", tags=["occupations"])
api_router.include_router(character.router, prefix="/characters", tags=["characters"])
api_router.include_router(nfc.router, prefix="", tags=["nfc"])
api_router.include_router(achivement.router, prefix="/achivements", tags=["achivements"])
api_router.include_router(event.router, prefix="/events", tags=["events"])
