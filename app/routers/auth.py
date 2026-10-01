from fastapi import APIRouter, Depends , HTTPException
from app.schemas import(
    RegisterRequest,
    LoginResponse,
    LoginRequest,
    RefreshRequest
)
from app.database import get_db
from sqlalchemy.orm import Session
from app.models import User, RefreshToken

from datetime import datetime,timezone, timedelta

from app.security import(
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    REFRESH_TOKEN_EXPIRE_DAYS   
)

from jose import jwt,JWTError
from app.security import SECRET_KEY,ALGORITHM



router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User).filter(User.email == request.email).first()
    )

    if existing_user:
        raise HTTPException(
            status_code = 400,
            detail="email is already registered"

        )

    password_hash  = hash_password(
        request.password
    )

    user = User(
        email = request.email,
        password_hash = password_hash,
        # role = "user"
    )

    db.add(user)
    db.commit()
    db.refresh(user)


    return {
        "message": "User registered successfully",
        "user_id": user.id
    }



@router.post(
    "/login",
    response_model=LoginResponse
) 
def login(
    request:LoginRequest,
    db: Session = Depends(get_db)
):

    user = (
        db.query(User).filter(User.email == request.email).first()
    )    

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    password_valid = verify_password(
        request.password,
        user.password_hash
    )

    if not password_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token  = create_access_token(
        user.id
        # user.role
    )

    refresh_token = create_refresh_token(
        user.id
    )

    expires_at = (
        datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )

    refresh_token_record = RefreshToken(
        user_id = user.id,
        token = refresh_token,
        expires_at = expires_at,
        revoked = False
    )

    db.add(refresh_token_record)
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


# @router.post("/refresh")
# def auth_refresh(
#     request: RefreshRequest,
#     db: Session = Depends(get_db)
# ):
#     try:
#         payload = jwt.decode(
#             request.refresh_token,
#             SECRET_KEY,
#             algorithms=ALGORITHM
#         )

#         #make sure this is actalluy refresh token
#         if payload.get("type") != "refresh":
#             raise HTTPException(
#                 status_code=401,
#                 detail="Invalid refresh token"
#             )

#         user_id = payload.get("sub")

#         if user_id is None:
#             raise HTTPException(
#                 status_code=401,
#                 detail="Invalid refresh token"
#             )

#         user = (
#             db.query(User).filter(User.id == int(user_id)).first()
#         )

#         if not user :
#             raise HTTPException(
#                 status_code=401,
#                 detail="user not found"

#             )

#         new_access_token = create_access_token(
#             user.id
#         )

#         return {
#             "access_token" : new_access_token,
#             "token_type" : "bearer"
#         }
    
#     except(JWTError,ValueError):
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid or expired refresh token"
#         )


@router.post("/refresh")
def refresh_token(
    request:RefreshRequest,
    db: Session = Depends(get_db)
):
    try:

        payload = jwt.decode(
            request.refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]

        )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )

        user_id  = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )

        refresh_token_record = (
            db.query(RefreshToken)
            .filter(
                RefreshToken.token == request.refresh_token,
                RefreshToken.user_id == int(user_id),
                RefreshToken.revoked == False

            )
            .first()
        )

        if not refresh_token_record:
            raise HTTPException(
                status_code=401,
                detail="Refresh token is invalid or revoked"
            )

        if refresh_token_record.expires_at < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=401,
                detail="Refresh token is expired"
            )
        
        user = (
             db.query(User).filter(User.id == int(user_id)).first()
         )

        if not user:
            raise HTTPException(
                status_code=401,
                detail="user not found"
            )

        new_access_token = create_access_token(user.id)

        return{
            "access_token" : new_access_token,
            "token_type" : "bearer"

        }

    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token"
        )



@router.post("/logout")
def logout(
    request:RefreshRequest,
    db:Session = Depends(get_db)

):
    refresh_token_record = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == request.refresh_token,
            RefreshToken.revoked == False
        )
        .first()
    )

    if not refresh_token_record:
        raise HTTPException(
            status_code=401,
            detail="Invalid or already revoked refresh token"
        )

    refresh_token_record.revoked = True

    db.commit()

    return{
        "message":"Logged out successfully"
    }