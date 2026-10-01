from fastapi import APIRouter, Depends
from app.models import User
from app.routers.users import ( get_current_user,require_role)
from app.permissions import require_permission



router = APIRouter(
    prefix="/protected",
    tags=["Protected"]
)


@router.get("/admin")
def admin_point(
    current_user:User = Depends(require_role("admin"))
):
    return {
        "message": "Welcome Admin",
        "user_id": current_user.id,
        # "role" : current_user.role
    }


@router.get("/medical")
def medical_endpoint(
    current_user :User = Depends(require_role("admin","doctor"))
):
    return{
        "message": "Medical Api granted",
        "user_id" : current_user.id,
        # "role": current_user.role
    }


@router.get("/patients")
def get_patient(
    current_user:User = Depends(
        require_permission("patient:read")
    )
):
    return{
        "message":"patient List accessed",
        "user_email": current_user.email,
        # "role": current_user.role
    }


@router.delete("/patients/{patient_id}")
def delete_patient(
    patient_id: int,
    current_user: User = Depends(
        require_permission("patient:delete")
    )
):
    return {
        "message": "Patient deleted",
        "patient_id": patient_id,
        "deleted_by": current_user.email,
        # "role": current_user.role
    }


@router.get("/hello")
def protected_hello(
    current_user : User = Depends(get_current_user)
):
    return{
        "message" : f"Hello {current_user.email}",
        "user_id" : current_user.id
    }