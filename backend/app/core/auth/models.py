import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.models import Base, BaseModelMixin, UserModelMixin


class User(Base, BaseModelMixin, UserModelMixin):
    __tablename__ = 'users'

    def __repr__(self):
        return f'<User {self.email}>'
