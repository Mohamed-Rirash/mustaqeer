from fastapi import APIRouter
from ..services.my_Progress_service import (
    get_user_progress,
    submit_progress
)
from ..config.dependencies import db_dependency
from  ..config.security import user_dependency
from ..responses.myprogress_response import MyProgressResponse
from ..schemas.my_progress_request import MyProgress
router = APIRouter(
    prefix="/progress",
    tags=["Progress"]
)
#TODO-1: CREATE ROUTE FOR GETTING READING PROGRESS THAT STARTS FROM FIRST Juz FIRST XISBI FIRST CHAPTER FIRST VERSE
@router.get("/",response_model=MyProgressResponse)
async def get_my_progress(db: db_dependency, user: user_dependency):
    return await get_user_progress(db, user)


# @router.get("/progress/{episode_id}",response_model=Episode_progress)
# async def get_episode_progress(db: db_dependency, user: user_dependency, episode_id: int):
#     return await fetch_episode_progress(db, user, episode_id)

#TODO-2: CREATE ROUTE FOR ALLOWING USER TO SEND THEIR PROGRESS EACH DAY WE EXPECT THEM TO SEND IT AT ONCE A DAY AND WE UPDATE THE INITIAL STARTING POINT BASED ON THE EPISODE THE USER IS IN
@router.post("/read/{episode_id}")
async def create_reading_progress(data: MyProgress, episode_id: int, db: db_dependency, user: user_dependency):
    return await submit_progress(db, user, episode_id, data)
#TODO-2.1: EVRY DAY WE EXPECT THE USER TO SEND THE PROGRESS, WE WILL STORE IT IN OUR DATABASE AND WE WILL UPDATE THE PROGRESS TO WHERE USER IS NOW E.G: HE START FORM 1ST JUS AND WE ADD THE REQUIRED AMOUNT OF VERSES WE EXPECTED BASED ON THE EPISODE THE USER IS IN

#TODO-2.2: IF THE USER MISSING PART OF THE REQUIRED AMOUNT OF QURAN READING IN THAT DAY, WE WILL STORE IT IN REMAINED FIELD AND WE WILL ADD IT IN THE NEXT DAY (FOR EXAMPLE IF HE SHOULD READ 2 JUZ BUT HE ONLY READ 1, WE WILL STORE THE REMAINED JUZ OR XISBI IN REMAINED FIELD AND WE WILL ADD IT IN THE NEXT DAY)
