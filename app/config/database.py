import contextlib
from app.config.settings import settings
from typing import AsyncIterator
from sqlalchemy.orm import declarative_base
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    AsyncConnection,
    async_sessionmaker
)

Base = declarative_base()

class DatabaseSessionManager:
     def __init__(self, host: str, engine_kwargs: dict[str] = {}):
        """
        Initialize the database session manager.

        This method is used to initialize the database session manager. It
        creates an async engine and an async session maker.

        Args:
            host (str): The database connection URI.
            engine_kwargs (dict[str]): Additional keyword arguments to pass
                to the `create_async_engine` function.
        """
        # Create an async engine, which is an instance of the
        # sqlalchemy.ext.asyncio.AsyncEngine class. This is an async version
        # of the standard Engine class.
        self._engine = create_async_engine(
            host,
            # Set the pool class to NullPool, which is a special pool class
            # that does not pool connections. This is useful for testing, as
            # it allows you to easily test the database code without having to
            # worry about connections being returned to the pool.
            poolclass=NullPool,
            # Pass any additional keyword arguments to the create_async_engine
            # function.
            **engine_kwargs
        )
        # Create an async session maker, which is an instance of the
        # sqlalchemy.ext.asyncio.async_sessionmaker class. This is an async
        # version of the standard sessionmaker class.
        self._sessionmaker = async_sessionmaker(
            # Set the autocommit argument to False, which means that the session
            # will not automatically commit any changes.
            autocommit=False,
            # Set the bind argument to the async engine, which means that the
            # session will use the engine to connect to the database.
            bind=self._engine,
            # Set the expire_on_commit argument to False, which means that the
            # session will not expire any objects that are changed when a commit
            # is made. This is useful for testing, as it allows you to easily
            # test the database code without having to worry about objects being
            # expired.
            expire_on_commit=False
        )
     def init(self, host: str):
        """
        Initialize the database session manager.

        This method is used to initialize the database session manager. It
        creates an async engine and an async session maker.

        Args:
            host (str): The database connection URI.

        Notes:
            This method is used by the application to create a database session
            manager. It is called once when the application is started.

            The async engine is created using the `create_async_engine` function
            from `sqlalchemy.ext.asyncio`. The `poolclass` argument is set to
            `NullPool`, which means that the engine will not use a connection pool.
            This is useful for testing, as it allows you to easily test the
            database code without having to worry about connections being
            returned to the pool.

            The async session maker is created using the `async_sessionmaker`
            function from `sqlalchemy.ext.asyncio`. The `autocommit` argument is
            set to `False`, which means that the session will not automatically
            commit any changes. The `bind` argument is set to the async engine,
            which means that the session will use the engine to connect to the
            database. The `expire_on_commit` argument is set to `False`, which
            means that the session will not expire any objects that are changed
            when a commit is made. This is useful for testing, as it allows you
            to easily test the database code without having to worry about
            objects being expired.
        """
        self._engine = create_async_engine(host, poolclass=NullPool)
        self._sessionmaker = async_sessionmaker(
            autocommit=False, bind=self._engine, expire_on_commit=False
        )


     async def close(self):
        """
        Close the database session manager.

        This method closes the database session manager and releases any resources
        associated with it. After calling this method, the session manager should
        not be used anymore.

        Raises:
            Exception: If the session manager is not initialized.
        """
        # Check if the session manager is initialized
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        # Dispose of the engine, releasing any resources associated with it
        await self._engine.dispose()

        # Remove the engine and session maker references, so that this object can be
        # garbage collected
        self._engine = None
        self._sessionmaker = None


     @contextlib.asynccontextmanager
     async def connect(self) -> AsyncIterator[AsyncConnection]:
        """
        Asynchronously connect to the database and yield an async connection.

        This method is an async context manager that connects to the database
        and yields an `AsyncConnection` object. The connection is automatically
        rolled back if an exception is raised while the context manager is
        active. If no exception is raised, the connection is automatically
        committed when the context manager is exited.

        Note that this method assumes that the database session manager has
        already been initialized. If the database session manager is not
        initialized, an exception will be raised.

        Yields:
            AsyncIterator[AsyncConnection]: An async connection to the database.
        """
        # Check if the session manager is initialized
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        # Start a database transaction
        async with self._engine.begin() as connection:
            try:
                # Yield the connection to the caller
                yield connection
            except Exception:
                # If an exception is raised, rollback the transaction
                await connection.rollback()
                # Reraise the exception
                raise


     @contextlib.asynccontextmanager
     async def session(self) -> AsyncIterator[AsyncSession]:
        """
        Asynchronously create a session and yield an async session object.

        This method is an async context manager that creates a session and
        yields an `AsyncSession` object. The session is automatically
        rolled back if an exception is raised while the context manager is
        active. If no exception is raised, the session is automatically
        committed when the context manager is exited.

        Note that this method assumes that the database session manager has
        already been initialized. If the database session manager is not
        initialized, an exception will be raised.

        Yields:
            AsyncIterator[AsyncSession]: An async session to the database.
        """

        # Check if the session manager is initialized
        if self._sessionmaker is None:
            # If the session manager is not initialized, raise an exception
            raise Exception("DatabaseSessionManager is not initialized")

        # Create an async session using the session maker
        session = self._sessionmaker()

        try:
            # Yield the session to the caller
            yield session
        except Exception:
            # If an exception is raised, rollback the session
            await session.rollback()
            # Reraise the exception
            raise
        finally:
            # When the context manager is exited, close the session
            await session.close()


            # This method is used to create all tables in the database.
            # The tables are defined in the `Base` class, which is a subclass of `declarative_base`.
            # The `create_all` method is used to create all tables defined in the `Base` class.
            # The `create_all` method takes a `bind` argument, which is the database connection to use.
            # In this case, we are using an async connection, which is passed as the `connection` argument.
            # The `create_all` method is called on the `metadata` object of the `Base` class,
            # which is an instance of `MetaData`.
            # The `create_all` method executes SQL statements to create all tables in the database.
            # The `run_sync` method is used to execute the sync version of the `create_all` method
            # on the async connection.
            # The `run_sync` method is used to execute a sync function on an async object.
            # The sync function is executed in a thread pool, so it can block, but it is executed
            # in a separate thread from the event loop, so it does not block the event loop.
     async def create_all(self, connection: AsyncConnection):
        # Execute the sync version of the `create_all` method on the async connection.
        # This is done using the `run_sync` method.
        # The `run_sync` method takes a sync function and a list of arguments to pass to the function.
        # The sync function is `Base.metadata.create_all`, which is a sync function that creates all tables in the database.
        # The `connection` object is passed as an argument to the sync function.
        await connection.run_sync(Base.metadata.create_all)

        # This method is used to drop all tables in the database.
        # The tables are defined in the `Base` class, which is a subclass of `declarative_base`.
        # The `drop_all` method is used to drop all tables defined in the `Base` class.
        # The `drop_all` method takes a `bind` argument, which is the database connection to use.
        # In this case, we are using an async connection, which is passed as the `connection` argument.
        # The `drop_all` method is called on the `metadata` object of the `Base` class,
        # which is an instance of `MetaData`.
        # The `drop_all` method executes SQL statements to drop all tables in the database.
        # The `run_sync` method is used to execute the sync version of the `drop_all` method
        # on the async connection.
        # The `run_sync` method is used to execute a sync function on an async object.
        # The sync function is executed in a thread pool, so it can block, but it is executed
        # in a separate thread from the event loop, so it does not block the event loop.
     async def drop_all(self, connection: AsyncConnection):
        # Execute the sync version of the `drop_all` method on the async connection.
        # This is done using the `run_sync` method.
        # The `run_sync` method takes a sync function and a list of arguments to pass to the function.
        # The sync function is `Base.metadata.drop_all`, which is a sync function that drops all tables in the database.
        # The `connection` object is passed as an argument to the sync function.
        await connection.run_sync(Base.metadata.drop_all, connection)



sessionmanager = DatabaseSessionManager(settings.DATABASE_URI, {"echo": True})
