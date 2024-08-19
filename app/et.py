from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.database import sessionmanager
from app.config.settings import settings

version = "0.0.1"

sessionmanager.init(settings.DATABASE_URI)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if sessionmanager._engine is not None:
        await sessionmanager.close()


app = FastAPI(
    title="mustaqeer",
    desscription="app that motivates you to read quran and track your quran progress also has ranking system",
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

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    async with sessionmanager._engine.begin() as conn:
        await sessionmanager.create_all(conn)


@app.get("/")
def read_root():
    return {"Hello": "World"}
