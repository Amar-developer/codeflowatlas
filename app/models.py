from sqlalchemy import Column, Integer, String,ForeignKey, UniqueConstraint,DateTime,Boolean
from app.database import Base


 
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key = True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String,nullable=False)
    # role = Column(String, default= "user",nullable=False,server_default="user")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer,primary_key=True)
    name = Column(String,unique=True,nullable=False)


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer,primary_key=True)
    name = Column(String, unique=True, nullable=False)



class UserRole(Base):
    __tablename__ = "user_roles"

    id = Column(Integer,primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),nullable=False)
    role_id = Column(Integer,ForeignKey("roles.id", ondelete="CASCADE"),nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "role_id",
            name="uq_user_role"
        ),
    )


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer,primary_key=True)

    role_id = Column(Integer,ForeignKey("roles.id",ondelete="CASCADE"),nullable=False)
    permission_id = Column(Integer,ForeignKey("permissions.id",ondelete="CASCADE"),nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "role_id",
            "permission_id",
            name="uq_role_permission"
        ),
    )


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"   

    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(
        Integer,ForeignKey("users.id",ondelete="CASCADE"),
        nullable=False
    ) 

    token =  Column(String, unique=True, nullable=False)
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False
        )
    revoked = Column(Boolean, default=False, nullable=False)