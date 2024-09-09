from fastapi import APIRouter, HTTPException, status
from app.config.dependencies import db_dependency
from app.config.security import user_dependency
from app.services.episodes import create_episode, exit_episode_service, get_all_episodes_service, get_episode_by_id_service, get_episode_by_juz_service, get_episode_members_service, join_episode_service
from app.schemas.episodes import AddEpisodeRequest, JoinEpisodeRequest
from app.responses.episodes import AddEpisodeResponse

episode_router = APIRouter(
    prefix="/episodes",
    tags=["Episodes"],
    responses={401: {"description": "Unauthorized"}}
)


@episode_router.post("/add", response_model=AddEpisodeResponse)
async def add_episode(data: AddEpisodeRequest, db: db_dependency, user: user_dependency):
    return await create_episode(data, db, user)

@episode_router.post("/join", status_code=status.HTTP_201_CREATED)
async def join_episode(data: JoinEpisodeRequest, db: db_dependency, user: user_dependency):
    return await join_episode_service(data, db, user)

@episode_router.get("/episodes", status_code=status.HTTP_200_OK)
async def get_all_episodes(db: db_dependency):
    return await get_all_episodes_service(db )

@episode_router.get("/episodes/{episode_id}", status_code=status.HTTP_200_OK)
async def get_episode_by_id(episode_id: int, db: db_dependency):
    return await get_episode_by_id_service(episode_id, db)

@episode_router.get("/episode_members/{episode_id}", status_code=status.HTTP_200_OK)
async def get_episode_members(episode_id: int, db: db_dependency):
    return await get_episode_members_service(episode_id, db)

@episode_router.get("/episodes/{episode_juz}", status_code=status.HTTP_200_OK)
async def get_episode_by_juz(episode_juz: int, db: db_dependency):
    episode = await get_episode_by_juz_service(episode_juz, db)
    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")
    return episode

@episode_router.delete("/exit/{episode_id}", status_code=status.HTTP_204_NO_CONTENT)
async def exit_episode(episode_id: int, db: db_dependency, user: user_dependency):
    return await exit_episode_service(episode_id, db, user)
