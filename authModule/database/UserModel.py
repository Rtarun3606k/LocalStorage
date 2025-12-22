from sqlalchemy import Column, Integer, String, Index
from datetime import datetime, timezone
from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class UserModel(db.Model):
    __tablename__ = "user_table"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
    dataOfBirth = Column(String(200), nullable=True)
    passwordHash = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, unique=True, index=True)
    createdAt = Column(
        String(200),
        nullable=True,
        default=lambda: datetime.now(timezone.utc).isoformat(),
    )
    updatedAt = Column(
        String(200),
        nullable=True,
        onupdate=lambda: datetime.now(timezone.utc).isoformat(),
        default=lambda: datetime.now(timezone.utc).isoformat(),
    )

    def __repr__(self):
        return f"<UserModel(id={self.id}, name={self.name}, email={self.email})>"
