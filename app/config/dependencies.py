from fastapi import Depends
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncIterator
from app.config.database import sessionmanager



async def get_db() -> AsyncIterator[AsyncSession]:
    """
    This function returns a database session dependency.

    The function is an async generator, which means it returns an async iterator.
    The async iterator yields an `AsyncSession` object, which is a database session.

    The `sessionmanager.session()` context manager is used to create a database session.
    The `sessionmanager.session()` context manager takes care of creating and closing the database session.
    The `sessionmanager.session()` context manager is an async context manager, which means it must be used with an `async with` statement.

    The `yield session` statement yields the `session` object to the caller.
    The `yield session` statement is inside an `async with` statement, which means that the `session` object is automatically closed when the `async with` statement is exited.

    The `yield session` statement is used to provide a database session to FastAPI's dependency injection system.
    The `yield session` statement is used to provide a database session to the route handlers that depend on this function.
    The `yield session` statement is used to provide a database session to the route handlers that depend on this function.
    """

    async with sessionmanager.session() as session:
        yield session


db_dependency = Annotated[AsyncSession, Depends(get_db)]
# cache_dependency = Annotated[AsyncSession, Depends(get_db)]
# user_dependency = Annotated[AsyncSession, Depends(get_db)]
