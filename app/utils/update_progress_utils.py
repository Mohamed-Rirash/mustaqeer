from datetime import datetime, time, timedelta
from sqlalchemy import select, func
from app.models.episodes import Episode
from app.models.my_progress_model import Progress
from app.services.episodes import exit_episode_service

async def update_juz_count(db):
    # Get current time in UTC
    now = datetime.utcnow()

    # Check if it's midnight UTC (00:00)
    if now.time() == time(0, 0):
        # Query to get all active episodes
        active_episodes_query = select(Episode)
        active_episodes_result = await db.execute(active_episodes_query)
        active_episodes = active_episodes_result.scalars().all()

        # Iterate through each active episode
        for episode in active_episodes:
            # Query to get all progress entries for this episode (excluding dropped users)
            progress_query = select(Progress).where(
                Progress.episode_id == episode.id,
                Progress.state != "droped"
            )
            progress_result = await db.execute(progress_query)
            progress_entries = progress_result.scalars().all()

            # Update progress for each user in the episode
            for progress in progress_entries:
                # Check if the user is in this specific episode
                if progress.episode_id == episode.id:
                    # Increase the 'remained' count by the episode's juz number
                    progress.juz_required += episode.juz
                    # Update the submission time to now
                    progress.submission_time = now

                # Check if the user should be dropped from the episode
                if progress.juz_required >= 6:
                    # Reset user's progress and mark as dropped
                    progress.juz_required = 0
                    progress.juz_readed = 0
                    progress.remained = 0
                    progress.xp = 0
                    progress.state = "droped"
                    # Remove user from the episode
                    await exit_episode_service(episode.id, db, progress.user)

            # Calculate and update the episode's overall progress
            if episode.progress + episode.juz > 30:
                # Increment the number of khatmis
                episode.no_of_khatmis += 1
                # Reset the progress, keeping any overflow
                episode.progress = 0
            else:
                # Increment progress based on the episode's juz
                episode.progress += episode.juz

            # Commit all changes to the database
            await db.commit()
