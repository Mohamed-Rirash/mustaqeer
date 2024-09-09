
from urllib.parse import urlparse
import uuid
import magic
from sqlalchemy import select, bindparam, func
from fastapi import HTTPException, status
from app.config.security import (
        get_token_payload,
        is_password_strong_enough,
        hash_password,
        load_user,
        verify_password,
        str_encode,
        str_decode,
        generate_token
        )
from app.models.users import (
    User,
    UserToken
)
from fastapi.responses import JSONResponse
from app.config.security import hash_password
from app.services.email import send_account_verification_email, send_password_reset_email
from app.utils.profile import (
    MB,
    SUPPORTED_IMAGE_FORMATS,
    delete_s3_image,
    s3_upload
)
from app.utils.string import unique_string
from sqlalchemy.orm import joinedload

# 2
from app.utils.email_context import FORGOT_PASSWORD, USER_VERIFY_ACCOUNT
from app.config.security import (
    verify_password
)
from datetime import datetime

from app.services.email import send_account_activation_confirmation_email
from sqlalchemy.exc import IntegrityError
from datetime import timedelta, datetime
from app.config.settings import settings




async def create_user(data, background_tasks, db):
    """
    Create a new user.

    This function performs the following steps:
    1. Starts a transaction.
    2. Checks if the user already exists.
    3. Validates the password strength.
    4. Creates a new user.
    5. Adds the new user to the database.
    6. Refreshes the user object.
    7. Sends an account verification email.

    If any of the above steps fail, the transaction is rolled back and an HTTPException is raised.
    """


    try:
        # Start a transaction
        async with db.begin():

            # Check if the user already exists

            query = select(User).where(User.email == bindparam("email"))
            user = await db.execute(
                query,
                {"email": data.email},
            )

            user_exit = user.scalars().first()
            if user_exit:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="The user with this email already exists. Please try to login instead.",
                )

            # Validate password strength
            if not is_password_strong_enough(data.password):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password must contain at least 8 characters, including one uppercase letter, one lowercase letter, one number, and one special character.",
                )

            # Create a new user
            new_user = User(
                first_name=data.first_name,
                last_name=data.last_name,
                email=data.email,
                password=hash_password(data.password),
                is_active=False,
                is_firstlogin=False,
                is_superuser=False,
                created_at=func.now(),
            )

            # Add the new user to the database
            db.add(new_user)

            # The commit will be handled automatically when the context manager exits

        # Now that the transaction is complete, refresh the user object
        await db.refresh(new_user)

        # Send the account verification email
        try:
            await send_account_verification_email(
                user=new_user, background_tasks=background_tasks
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User created, but failed to send verification email. Please contact support.",
            )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "User created successfully. Please check your email for verification."
            },
        )

    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User creation failed due to a database error. Please try again.",
        )

    except HTTPException as http_exc:
        await db.rollback()
        raise http_exc

    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during user creation. Please try again later.",
        )

async def activate_user_account(data, db, background_tasks):
    """
    Activate a user account given an activation token and an email address.

    This function will:
    1. Retrieve the user by email.
    2. Verify the token.
    3. Activate the user account.
    4. Send an account activation confirmation email.

    If an error occurs, the transaction is rolled back and an HTTPException is raised.
    """
    try:
        async with db.begin():
            # Retrieve the user by email
            query = select(User).where(User.email == bindparam("email"))
            user_result = await db.execute(query, {"email": data.email})
            user_result = user_result.scalars().first()

            if not user_result:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This link is not valid. Please double-check your email address.",
                )

            # Verify the token
            user_token = user_result.get_context_string(context=USER_VERIFY_ACCOUNT)
            try:
                token_valid = verify_password(user_token, data.token)
            except Exception:
                token_valid = False

            if not token_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This link either expired or is not valid. Please try again.",
                )

            # Activate the user account
            user_result.is_active = True
            user_result.updated_at = datetime.utcnow()
            user_result.verified_at = datetime.utcnow()

            # Add and refresh the user instance
            db.add(user_result)
            await db.flush()  # Not usually awaited, but for completeness

            # Commit is handled by the async with context manager

        # Send the account activation confirmation email
        try:
            await send_account_activation_confirmation_email(user_result, background_tasks)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User activated, but failed to send confirmation email. Please contact support.",
            )

        return user_result

    except IntegrityError:
        # Rollback is not needed here as async with db.begin() will handle it
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to activate user account due to a database error. Please contact support.",
        )

    except HTTPException as http_exc:
        # Rollback is not needed here as async with db.begin() will handle it
        raise http_exc

    except Exception as exc:
        # Rollback is not needed here as async with db.begin() will handle it
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during account activation. Please try again later.",
        )
async def upload_profile(profile_image, db, user):

    if not profile_image:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No profile image provided")

    # Read the image content
    content = await profile_image.read()
    size = len(content)

    if size > 1 * MB:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Profile image is too large")

    file_type = magic.from_buffer(content, mime=True)
    if file_type not in SUPPORTED_IMAGE_FORMATS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported image format")

    filename = f"{uuid.uuid4()}.{SUPPORTED_IMAGE_FORMATS[file_type]}"

    user_id = user.id
    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user token")

    # Fetch the user from the database
    user = await db.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()

    if user:
        # Check if there is an existing profile image
        if user.profile_image:
            # Extract the filename from the existing URL
            existing_url = user.profile_image
            parsed_url = urlparse(existing_url)
            existing_filename = parsed_url.path.lstrip('/')  # Remove leading '/'

            # Delete the existing image from S3
            await delete_s3_image(existing_filename)

        # Upload the new image to S3
        await s3_upload(content=content, filename=filename, content_type=file_type)

        # Construct the new image URL
        image_url = f"https://{settings.AWS_S3_BUCKET_NAME}.s3.amazonaws.com/{filename}"

        # Update the profile image URL in the database
        user.profile_image = image_url
        await db.commit()  # Commit the transaction to save the changes
        await db.flush()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return {"message": "Profile image uploaded successfully", "image_url": image_url}


async def get_login_token(data, db, response):
    user = await load_user(data.username, db)

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="This email is not associated with any registered account")

    if not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account is not active")

    if not user.verified_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account is not verified")
    return await _generate_tokens(user, db, response)


async def _generate_tokens(user, db, response):
    refresh_key = unique_string(100)
    access_key = unique_string(50)
    rt_expires = timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    user_token = UserToken(
        user_id=user.id,
        refresh_token=refresh_key,
        access_token=access_key,
        expires_at=datetime.utcnow() + rt_expires,
        created_at=datetime.utcnow(),
    )

    db.add(user_token)
    await db.commit()
    await db.flush()  # Flush changes to the database without committing

    at_payload = {
        "sub": str_encode(str(user.id)),
        "a": access_key,
        "r": str_encode(str(user_token.id)),
        "n": str_encode(f"{user.first_name}"),
    }

    at_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = generate_token(at_payload, settings.JWT_SECRET, settings.JWT_ALGORITHM, at_expires)

    rt_payload = {
        "sub": str_encode(str(user.id)),
        "t": refresh_key,
        "a": access_key,
    }
    refresh_token = generate_token(rt_payload, settings.JWT_SECRET, settings.JWT_ALGORITHM, rt_expires)

    one_day = timedelta(days=1)
    expiry_time = datetime.utcnow() + one_day
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=int(one_day.total_seconds()),
        expires=expiry_time.strftime("%a, %d-%b-%Y %H:%M:%S GMT"),
        samesite="none",
        secure=False  # Set to False during development if not using HTTPS
    )

    return {
        "access_token": access_token,
        "expires_in": int(at_expires.total_seconds())
    }


async def get_refresh_token(request, response, db):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No refresh token provided")

    # Extract and validate the token payload
    token_payload = get_token_payload(
        refresh_token, settings.JWT_SECRET, settings.JWT_ALGORITHM)
    if not token_payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token."
        )

    refresh_key = token_payload.get("t")
    access_key = token_payload.get("a")
    user_id = token_payload.get("sub")

    async with db.begin():  # Start a transaction
        query = select(UserToken).options(joinedload(UserToken.user)).filter(
            UserToken.refresh_token == refresh_key,
            UserToken.access_token == access_key,
            UserToken.user_id == user_id,
            UserToken.expires_at > datetime.utcnow(),
        )

        user_token = await db.execute(query).scalars().first()

        if not user_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token."
            )

        # Update the expiration time of the user token
        user_token.expires_at = datetime.utcnow(
        ) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)

        # No need to call db.add(user_token) if you are just updating the existing entity
        await db.flush()  # Flush changes to the database

    # Generate new tokens for the user
    return await _generate_tokens(user_token.user, db, response)


async def email_forgot_password_link(data, background_tasks, db):
    user = await load_user(data.email, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="This email is not associated with any registered account")
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account is not active")
    if not user.verified_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Account is not verified")
    await send_password_reset_email(user, background_tasks)


async def reset_user_password(data, db):
   user = await load_user(data.email, db)
   if not user:
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                           detail="This email is not associated with any registered account")
   if not user.is_active:
       raise HTTPException(
           status_code=status.HTTP_400_BAD_REQUEST, detail="Account is not active")
   if not user.verified_at:
       raise HTTPException(
           status_code=status.HTTP_400_BAD_REQUEST, detail="Account is not verified")

   user_token = user.get_context_string(context=FORGOT_PASSWORD)
   token_valid = verify_password(user_token, data.token)
   if not token_valid:
       raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token")

   user.password = hash_password(data.password)
   user.updated_at = datetime.now()

   await db.flush()


async def fetch_user_details(user_id, db):
    async with db.begin():
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return user
