from sqlalchemy import Boolean, Column, Integer, String, Enum
import enum
from app.core.database import Base

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
