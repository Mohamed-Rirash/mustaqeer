from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.database import sessionmanager
from app.config.settings import settings
from app.routes import users

version = "0.0.1"

sessionmanager.init(settings.DATABASE_URI)



@asynccontextmanager
async def lifespan(app: FastAPI):
    # async with sessionmanager._engine.begin() as conn:     # this is ok if you are not using alembic for migrations
    #     await sessionmanager.create_all(conn)
    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()

app = FastAPI(
    title="mustaqeer",
    description="app that motivates you to read quran and track your quran progress also has ranking system",
    version=version,
    lifespan=lifespan,
    docs_url="/api/{version}/docs"

)


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/")
def read_root():
    return {"Hello": "World"}


#TODO-1 TEST
from app.routes.test import test_router
app.include_router(test_router)
app.include_router(users.user_router)
app.include_router(users.guest_router)
app.include_router(users.auth_router)
