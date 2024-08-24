from fastapi import APIRouter, HTTPException, Request, status, BackgroundTasks, Depends, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select


from app.models.users import User
from app.responses.user import UserResponse
from app.schemas.users import EmailRequest, RegisterUserRequest, ResetRequest, VerifyUserRequest
from app.config.dependencies import db_dependency
from app.services import user
from fastapi.security import OAuth2PasswordRequestForm
from app.config.security import(oauth2_scheme, get_current_user,user_dependency)

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

auth_router = APIRouter(
    prefix="/users",
    tags=["Users"],
    responses={404: {"description": "Not found"}},

)


@user_router.post("/Signup", status_code=status.HTTP_201_CREATED)
async def register_new_user(
    data: RegisterUserRequest, background_tasks: BackgroundTasks, db: db_dependency
):
    return await user.create_user(data, background_tasks, db)


@user_router.post("/verify-account", status_code=status.HTTP_200_OK)
async def verify_user_account(
    data: VerifyUserRequest, background_tasks: BackgroundTasks, db: db_dependency
):
    await user.activate_user_account(data, db, background_tasks)
    return JSONResponse({"message": "Account is activated successfully."})


@guest_router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(
    response: Response, db: db_dependency, data: OAuth2PasswordRequestForm = Depends()
):
   return await user.get_login_token(data, db, response)
@guest_router.post("/logout", status_code=status.HTTP_200_OK)
async def logout_user(response: Response):
    response.delete_cookie(key="refresh_token")
    return JSONResponse({"message": "Logout successfully."})

@guest_router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_token(response: Response, request: Request, db: db_dependency):
    return await user.get_refresh_token(request, response, db)

@guest_router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(data: EmailRequest, background_tasks: BackgroundTasks, db: db_dependency):
    await user.email_forgot_password_link(data, background_tasks, db)
    return JSONResponse({"message": "Password reset link is sent to your email."})

@guest_router.put("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(data: ResetRequest,  db: db_dependency):
     await user.reset_user_password(data, db)
     return JSONResponse({"message": "Password reset successfully."})





@auth_router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def fetch_user(user=Depends(get_current_user)):
    return user


@auth_router.get("/{pk}", status_code=status.HTTP_200_OK, response_model=UserResponse)
async def get_user_info(id, db: db_dependency):
    return await user.fetch_user_details(id, db)
