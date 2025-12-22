from sqlalchemy import Column, ForeignKey, Integer, String, Index, Enum as SqlEnum
from datetime import datetime, timezone
from app import db
from enum import Enum
from sqlalchemy.dialects.postgresql import UUID
import uuid


class UserRoleEnum(Enum):
    Admin = "Admin"
    User = "User"
    Developer = "Developer"


class ServicesModel(db.Model):
    __tablename__ = "services_table"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)
    role = Column(SqlEnum(UserRoleEnum), nullable=False, default=UserRoleEnum.User)

    createdAt = Column(
        String(200), default=lambda: datetime.now(timezone.utc).isoformat()
    )
    updatedAt = Column(
        String(200),
        default=lambda: datetime.now(timezone.utc).isoformat(),
        onupdate=lambda: datetime.now(timezone.utc).isoformat(),
    )

    organizationId = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "organization_table.id", name="fk_services_organization", ondelete="CASCADE"
        ),
        nullable=False,
        index=True,
    )

    # Correct relationship name & backref
    organization = db.relationship(
        "OrganizationModel",
        backref=db.backref("services", lazy=True, cascade="all, delete-orphan"),
    )

    def __repr__(self):
        return f"<ServicesModel(id={self.id}, name={self.name})>"
