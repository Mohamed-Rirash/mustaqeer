from fastapi import  FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config.database import sessionmanager
from app.config.settings import settings
from app.routes import users

import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from app.config.settings import settings

version = "0.0.1"

sessionmanager.init(settings.DATABASE_URI)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # async with sessionmanager._engine.begin() as conn:     # this is ok if you are not using alembic for migrations
    #     await sessionmanager.create_all(conn)
    redis_connection = redis.from_url(settings.REDIS_URI, encoding="utf8")
    await FastAPILimiter.init(redis_connection)
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
async def index_get():
    return {"msg": "Hello World"}

#TODO-1 TEST
app.include_router(users.user_router)
app.include_router(users.guest_router)
app.include_router(users.profile_router)



# Existing imports and code...

# @app.get("/get-profile-image/{filename}")
# async def get_profile_image(filename: str):
#     try:
#         # Create a BytesIO stream to hold the image data
#         image_stream = io.BytesIO()

#         # Retrieve the object from S3
#         bucket.download_fileobj(Key=filename, Fileobj=image_stream)

#         # Move the stream position to the beginning
#         image_stream.seek(0)

#         # Get the content type based on the file extension
#         content_type = magic.from_file(filename, mime=True)

#         return StreamingResponse(image_stream, media_type=content_type)
#     except boto3.exceptions.S3UploadFailedError:
#         raise HTTPException(status_code=404, detail="Image not found")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Internal Server Error")
