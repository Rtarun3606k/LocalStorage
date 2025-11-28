from sqlalchemy import Column, Integer, String,Index 
from datetime import datetime,timezone
from app import db 
from sqlalchemy.dialects.postgresql import UUID
import uuid




class ApiKey(db.Model):
    __tablename__ = "api_keys"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = db.Column(db.String(36),db.ForeignKey("user_table.id", name="fk_apikey_user", ondelete="CASCADE"),nullable=False)

    service_id = db.Column(db.String(36),db.ForeignKey("services_table.id", name="fk_apikey_service", ondelete="CASCADE"),nullable=False)

    hashed_key = db.Column(db.String(255), nullable=False)  # Argon2 hash
    role = db.Column(db.String(50), nullable=False)         # inherited from UserService
    scopes = db.Column(db.JSON, default=list)               # ["read", "write"]

    revoked = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("UserModel", backref="api_keys")
    service = db.relationship("ServicesModel", backref="api_keys")


    def __repr__(self):
        return f"<ApiKey(id={self.id}, user_id={self.user_id}, service_id={self.service_id}, revoked={self.revoked})>"





