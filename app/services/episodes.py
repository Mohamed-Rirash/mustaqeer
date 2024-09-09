#TODO-1: CREATE EPISODE
from fastapi import HTTPException,status
from sqlalchemy import delete, func, select

from app.models.episodes import Episode, Member


async def create_episode(data, db, user):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")

    user_id = user.id

    # Check if the user is already a member of any episode
    query = select(Member).where(Member.user_id == user_id)
    existing_member = await db.execute(query)
    existing_member = existing_member.scalar_one_or_none()

    if existing_member:
        raise HTTPException(
            status_code=400,
            detail="You are already a member of an episode. Please exit your current episode before creating a new one."
        )

    # Initialize is_full to False by default
    is_full = False

    # Check if an active episode with the same juz already exists
    query = select(Episode).where(Episode.juz == data.juz.value, Episode.is_full == False)
    episode = await db.execute(query)
    episode = episode.scalar_one_or_none()

    if episode:
        # Check if the episode has reached the maximum number of members
        query = select(func.count(Member.id)).where(Member.episode_id == episode.id)
        member_count = await db.execute(query)
        member_count = member_count.scalar_one()

        # Allow creating a new episode if the current episode has 50 or more members
        if member_count < 50:
            raise HTTPException(status_code=400, detail="An active episode with fewer than 50 members already exists. Please join it instead of creating a new one.")

        # Set is_full to True if the current episode will be full after this user joins
        if member_count == 49:
            is_full = True

    # Create a new episode, with is_full now properly initialized
    new_episode = Episode(
        juz=data.juz.value,
        description=data.description,
        progress=0,
        is_full=is_full,
        user_id=user_id
    )
    db.add(new_episode)
    await db.commit()
    await db.flush()

    # Add the user as the first member of the new episode
    new_member = Member(
        user_id=user_id,
        episode_id=new_episode.id,
        joined_at=func.now(),
    )
    db.add(new_member)
    await db.commit()
    await db.flush()

    return new_episode

#TODO-2: Join Episode
async def join_episode_service(data, db, user):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")

    user_id = user.id

    # Check if the user is already a member of any episode
    query = select(Member).where(Member.user_id == user_id)
    existing_member = await db.execute(query)
    existing_member = existing_member.scalar_one_or_none()

    if existing_member:
        raise HTTPException(
            status_code=400,
            detail="You are already a member of an episode. Please exit your current episode before creating a new one."
        )

    # Check if the episode is active
    query = select(Episode).where(Episode.id == data.episode_id, Episode.is_full == False)
    episode = await db.execute(query)
    episode = episode.scalar_one_or_none()

    if not episode:
        raise HTTPException(status_code=404, detail="Episode not found or already full")

    # Check if the episode is in progress and less than 6 juz
    if episode.progress > 6:
        raise HTTPException(status_code=400, detail=" you can`t join this episode because you can not catch up with the progress of more than 6 juz")

    # Check if the episode has less than 50 members
    query = select(func.count(Member.id)).where(Member.episode_id == episode.id)
    member_count = await db.execute(query)
    member_count = member_count.scalar_one()

    if member_count >= 50:
        episode.is_full = True


    # Add the user to the episode
    new_member = Member(
        user_id=user_id,
        episode_id=episode.id,
        joined_at=func.now(),
    )
    db.add(new_member)
    await db.commit()
    await db.flush()

    return new_member


#CHECK IF THE EPISODE IS ACTIVE
#CHECK IF THE EPISODE IS IN PROGRESS OF LESS THEN 6 JUZ
#CHECK IF THE EPISODE IS IN PROGRESS OF LESS THEN 50 MEMBERS

#IF ALL OF THESE CONDITIONS ARE MET, ADD THE USER TO THE EPISODE

# add the user id to the members table



#TODO-2: Get Episode
async def get_all_episodes_service(db):
    query = select(Episode)
    episodes = await db.execute(query)
    episodes = episodes.scalars().all()
    return episodes

async def get_episode_by_juz_service(episode_juz, db):
    query = select(Episode).where(Episode.juz == episode_juz)
    episodes = await db.execute(query)
    episodes = episodes.scalars().all()
    return episodes

async def get_episode_by_id_service(episode_id, db):
    query = select(Episode).where(Episode.id == episode_id)
    episode = await db.execute(query)
    episode = episode.scalar_one_or_none()
    return episode

async def get_episode_members_service(episode_id, db):
    query = select(Member).where(Member.episode_id == episode_id)
    members = await db.execute(query)
    members = members.scalars().all()
    return len(members)





async def exit_episode_service(episode_id, db, user):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized User")

    user_id = user.id

    # Fetch the episode owned by the user, with members loaded
    query = (
        select(Episode)
        .where(Episode.id == episode_id)
    )
    episode_result = await db.execute(query)
    episode = episode_result.scalar_one_or_none()

    if not episode:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Episode not found")

    # Check if the user is a member of the episode
    member_query = select(Member).where(Member.episode_id == episode_id, Member.user_id == user_id)
    member_result = await db.execute(member_query)
    member = member_result.scalar_one_or_none()

    if not member:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a member of this episode")

    # Check the number of members in the episode
    member_count_query = select(func.count()).select_from(Member).where(Member.episode_id == episode_id)
    member_count = await db.execute(member_count_query)
    member_count = member_count.scalar()

    if member_count == 1:
        # If this is the last member, delete both the member and the episode
        delete_member_query = delete(Member).where(Member.episode_id == episode_id)
        await db.execute(delete_member_query)
        await db.delete(episode)
        await db.commit()
        return {"message": "Episode and last member deleted successfully"}
    else:
        # If not the last member, remove the current user from the episode's members
        delete_member_query = delete(Member).where(Member.episode_id == episode_id, Member.user_id == user_id)
        await db.execute(delete_member_query)
        await db.commit()
        return {"message": "User exited from the episode successfully"}

#TODO-3: Update Episode
#TODO-4: Delete Episode
#TODO-5: Get Episode by ID
#TODO-6: Get Episode by Juz
#TODO-7: Get Episode by Description
#TODO-8: Get Episode by Members No
#TODO-9: Get Episode by No of Khatmis
