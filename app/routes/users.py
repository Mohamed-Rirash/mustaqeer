from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status, BackgroundTasks, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select


from app.models.users import User
from app.responses.user import UserResponse
from app.schemas.users import EmailRequest, RegisterUserRequest, ResetRequest, VerifyUserRequest
from app.config.dependencies import db_dependency
from app.services.user import (
    create_user,
    activate_user_account,
    get_login_token,
    get_refresh_token,
    email_forgot_password_link,
    reset_user_password,
    fetch_user_details,
    upload_profile
)
from fastapi.security import OAuth2PasswordRequestForm
from app.config.security import (
    oauth2_scheme, get_current_user, user_dependency)
from fastapi_limiter.depends import RateLimiter

from app.services.profile import upload_profile_image


user_router = APIRouter(
    prefix="/user",
    tags=["Users"],
    responses={404: {"description": "Not found"}},
)


guest_router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
    responses={404: {"description": "Not found"}},
)



profile_router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
    responses={404: {"description": "Not found"}},
)


@user_router.post("/Signup", status_code=status.HTTP_201_CREATED)
async def register_new_user(
    data: RegisterUserRequest,
    background_tasks: BackgroundTasks,
    db: db_dependency,

):
    return await create_user(data, background_tasks, db)



@user_router.post("/verify-account", status_code=status.HTTP_200_OK)
async def verify_user_account(
    data: VerifyUserRequest, background_tasks: BackgroundTasks, db: db_dependency
):
    await activate_user_account(data, db, background_tasks)
    return JSONResponse({"message": "Account is activated successfully."})

@profile_router.put("/upload-profile-image", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=5, hours=24))])
async def upload_profile_pic(
    db: db_dependency,
    user: user_dependency,
    profile_image: UploadFile = File(...)
):
   return await upload_profile(profile_image=profile_image, db=db, user=user)

@guest_router.post("/login", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def login_user(
    response: Response,
    db: db_dependency,
    data: OAuth2PasswordRequestForm = Depends(),
):
    return await get_login_token(data, db, response)


@guest_router.post("/logout", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def logout_user(response: Response):
    response.delete_cookie(key="refresh_token")
    return JSONResponse({"message": "Logout successfully."})


@guest_router.post("/refresh", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def refresh_token(response: Response, request: Request, db: db_dependency):
    return await get_refresh_token(request, response, db)


@guest_router.post("/forgot-password", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def forgot_password(data: EmailRequest, background_tasks: BackgroundTasks, db: db_dependency):
    await email_forgot_password_link(data, background_tasks, db)
    return JSONResponse({"message": "Password reset link is sent to your email."})


@guest_router.put("/reset-password", status_code=status.HTTP_200_OK, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
async def reset_password(data: ResetRequest,  db: db_dependency):
    await reset_user_password(data, db)
    return JSONResponse({"message": "Password reset successfully."})


@profile_router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def fetch_user(user=Depends(get_current_user)):
    return user


@profile_router.get("/{pk}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user_info(id, db: db_dependency):
    return await fetch_user_details(id, db)
