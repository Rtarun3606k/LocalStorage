from sqlalchemy import Column, Integer, String,Index 
from datetime import datetime,timezone
from app import db 
from sqlalchemy.dialects.postgresql import UUID
import uuid
 




class UserService(db.Model):
    __tablename__ = "user_services"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(Integer, db.ForeignKey("user_table.id", name="fk_user_services_user", ondelete="CASCADE"), nullable=False)
    service_id = db.Column(Integer, db.ForeignKey("services_table.id", name="fk_user_services_service", ondelete="CASCADE"), nullable=False)

    role = db.Column(String(50), nullable=False)
    enabled = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("UserModel", backref="enabled_services")
    service = db.relationship("ServicesModel", backref="user_links")


