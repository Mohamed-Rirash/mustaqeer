


async def check_episode_condition(episode):
    conditions = [
        lambda e: e.is_active,
        lambda e: e.progress < 6,

    ]
    return all(condition(episode) for condition in conditions)
