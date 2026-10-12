# PERMISSIONS = {
#     "patient:read",
#     "patient:create",
#     "patient:update",
#     "patient:delete",

#     "appointment:read",
#     "appointment:create",
#     "appointment:update",
#     "appointment:delete",

#     "medical_record:read",
#     "medical_record:create",
#     "medical_record:update",
# }


# ROLE_PERMISSIONS = {
#     "admin": {
#         "patient:read",
#         "patient:create",
#         "patient:update",
#         "patient:delete",

#         "appointment:read",
#         "appointment:create",
#         "appointment:update",
#         "appointment:delete",

#         "medical_record:read",
#         "medical_record:create",
#         "medical_record:update",
#     },

#     "doctor": {
#         "patient:read",
#         "patient:update",

#         "appointment:read",
#         "appointment:create",
#         "appointment:update",

#         "medical_record:read",
#         "medical_record:create",
#         "medical_record:update",
#     },

#     "staff": {
#         "patient:read",
#         "patient:create",
#         "patient:update",

#         "appointment:read",
#         "appointment:create",
#         "appointment:update",
#     },

#     "pharmacist": {
#         "patient:read",
#     },

#     "lab_technician": {
#         "patient:read",
#         "medical_record:read",
#         "medical_record:create",
#     },
# }


from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Role, Permission, UserRole, RolePermission
from app.routers.users import get_current_user


def require_permission(required_permission : str):

    def permission_checker(
        current_user:User = Depends(get_current_user),
        db:Session = Depends(get_db)
    ):

        permission_exists = (
           db.query(Permission)
           .join(
                RolePermission,
                RolePermission.permission_id == Permission.id
            )
            .join(
                Role,Role.id == RolePermission.role_id
            )
            .join(
                UserRole,
                UserRole.role_id == Role.id
            )
            .filter(
                UserRole.user_id == current_user.id,
                Permission.name == required_permission
            )
            .first()

       )

        if not permission_exists:
          raise HTTPException(
             status_code=status.HTTP_403_FORBIDDEN,
             detail="You do not have permission to access this resource"
          )

        return current_user

    return permission_checker