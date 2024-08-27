from fastapi import APIRouter
from app.schemas.episodes import AddEpisodeRequest, AddEpisodeResponse
from app.config.dependencies import db_dependency
from app.config.security import user_dependency
router = APIRouter(prefix="/episodes",
                   tags=["Episodes"],
                   responses={401: {"description": "Unauthorized"}})

@router.post("/add", response_model=AddEpisodeResponse)
async def add_episode(data: AddEpisodeRequest, db: db_dependency, user: user_dependency):
    return {"message": "Episode added successfully"}
