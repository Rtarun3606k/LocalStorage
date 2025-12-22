from sqlalchemy import Column, ForeignKey, Integer, String, Index
from datetime import datetime, timezone
from app import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class OrganizationModel(db.Model):
    __tablename__ = "organization_table"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
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
        return f"<OrganizationModel (id={self.id}, name={self.name})>"
