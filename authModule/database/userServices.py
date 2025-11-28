from sqlalchemy import Column, Integer, String,Index 
from datetime import datetime,timezone
from app import db 
from sqlalchemy.dialects.postgresql import UUID
import uuid
 

class UserService(db.Model):
    __tablename__ = "user_services"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    

    user_id = db.Column(db.String(36),db.ForeignKey("user_table.id", name="fk_user_services_user", ondelete="CASCADE"),nullable=False)

    service_id = db.Column(db.String(36),db.ForeignKey("services_table.id", name="fk_user_services_service", ondelete="CASCADE"), nullable=False)
    role = db.Column(db.String(50), nullable=False)   # user role inside this service
    enabled = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # optional relationships
    user = db.relationship("UserModel", backref="enabled_services")
    service = db.relationship("UserService", backref="user_links")
