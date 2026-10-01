from fastapi import APIRouter, Depends , HTTPException , status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.security import get_current_user_id


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


def require_role(*allowed_roles: str):

    def role_checker(
            current_user:User = Depends(get_current_user)
    ):
        if current_user.role not in  allowed_roles :
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission access this resource"
            )

        return current_user

    return role_checker



def get_current_user(
        user_id: int = Depends(get_current_user_id),
        db: Session = Depends(get_db)
):
    user = (
        db.query(User).filter(User.id == user_id).first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="user not found"

        )

    return user



@router.get("/me")
def get_me(
    current_user:User = Depends(get_current_user)
):
    return{
        "id" : current_user.id,
        "email": current_user.email
    }


