from datetime import datetime
from itertools import count

from fastapi import HTTPException,status
from app.data.script import json_data
from app.models.my_progress_model import Progress
from app.models.episodes import Episode
from sqlalchemy import select, update

from app.services.episodes import exit_episode_service




async def get_user_progress(db, user):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
    # Check if the user has joined an episode
    episode_query = select(Episode).where(Episode.user_id == user.id)
    episode_result = await db.execute(episode_query)
    episode_result = episode_result.scalar_one_or_none()

    if episode_result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User has not joined any episode")

    query = select(Progress).where(Progress.user_id == user.id and Progress.juz != 30 and Progress.episode_id == episode_result.id)
    result = await db.execute(query)
    result = result.scalar_one_or_none()
    if result is None:
        result = Progress()
        result.juz = json_data[0]['juz']
        result.chapter = json_data[0]['chapter']
        result.verse = json_data[0]['verse']
        result.page = json_data[0]['pageNo']
        result.content = json_data[0]['content']
        result.submission_time = datetime.utcnow()
        result.juz_readed = 0
        result.remained = episode_result.juz
        result.state = "not_started"
        result.xp = 0
        result.user_id = user.id
        result.episode_id = episode_result.id
        db.add(result)
        await db.commit()
        await db.flush()


        return result

    return result


# async def fetch_episode_progress(db, user, episode_id):
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")
#     query = select(Episode).where(Episode.user_id == user.id and Episode.id == episode_id)
#     result = await db.execute(query)
#     result = result.scalar_one_or_none()
#     return result



async def submit_progress(db, user, progress, data):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

    # Check if the user has joined an episode
    episode_query = select(Episode).where(Episode.user_id == user.id)
    episode_result = await db.execute(episode_query)
    episode = episode_result.scalar_one_or_none()

    if episode is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User has not joined any episode")

    # Determine the juz count for the episode
    progress_query = select(Progress).where(Progress.user_id == user.id and Progress.juz != 30 and Progress.episode_id == episode.id)
    progress_result = await db.execute(progress_query)
    progress = progress_result.scalar_one_or_none()

    if not progress:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Progress not found")

    juz_count = progress.juz_required
    remaining_juz = progress.remained

    # Add carry-over if the user didn't finish the previous day
    if remaining_juz > 0:
        juz_count += remaining_juz

    # Check if the user is trying to submit more than allowed
    if data.readed_juz > juz_count:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Your max reading juz is {juz_count} today")

    # Update progress
    progress.remained = juz_count - data.readed_juz
    progress.xp += data.readed_juz * 10
    progress.juz_readed += data.readed_juz

    # If the user completes the required juz, mark as completed
    if progress.remained == 0:
        progress.state = "completed"
        progress.carry_over = 0  # No carry-over if all juz are completed
    else:
        progress.state = "active"
        progress.carry_over = progress.remained  # Carry over the remaining juz to the next day

    # Commit changes to the database
    await db.commit()
    await db.flush()

    return progress

# exept the user to submit maximum of the required juz
# 
