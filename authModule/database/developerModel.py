from sqlalchemy import Column, ForeignKey, Integer, String, Index
from datetime import datetime, timezone
from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class DeveloperModel(db.Model):
    __tablename__ = "developer_table"

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
    userId = Column(
        UUID(as_uuid=True),
        ForeignKey("user_table.id", name="fk_developer_user", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )  # foreign key to UserModel
    organizationId = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "organization_table.id", name="fk_developer_org", ondelete="CASCADE"
        ),
        nullable=False,
        index=True,
    )  # foreign key to OrganizationModel

    # relation with UserModel
    user = db.relationship(
        "UserModel",
        backref=db.backref("developers", lazy=True, cascade="all, delete-orphan"),
    )
    # relation with OrganizationModel
    organization = db.relationship(
        "OrganizationModel",
        backref=db.backref("developers", lazy=True, cascade="all, delete-orphan"),
    )

    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __repr__(self):
        return f"<DeveloperModel(id={self.id}, name={self.name}, email={self.email})>"
