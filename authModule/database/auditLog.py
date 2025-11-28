
from sqlalchemy import Column, Integer, String,Index 
from datetime import datetime,timezone
from app import db 
from sqlalchemy.dialects.postgresql import UUID
import uuid


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    api_key_id = db.Column(db.String(36),db.ForeignKey("api_keys.id", name="fk_auditlog_api_key", ondelete="CASCADE"),nullable=False)
    event = db.Column(db.String(50), nullable=False)  # created, revoked, used, failed_auth
    ip_address = db.Column(db.String(45), nullable=True)  # IPv4/IPv6
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    api_key = db.relationship("ApiKey", backref="audit_logs")
