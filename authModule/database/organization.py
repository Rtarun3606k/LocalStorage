from sqlalchemy import Column, ForeignKey, Integer, String,Index 
from datetime import datetime,timezone
from app import db 


class OrganizationModel(db.Model):
    __tablename__ = 'organization_table'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    createdAt = Column(String(200), nullable=True, default= lambda: datetime.now(timezone.utc).isoformat()) 
    updatedAt = Column(String(200), nullable=True, onupdate= lambda: datetime.now(timezone.utc).isoformat(),default= lambda: datetime.now(timezone.utc).isoformat())


    def __repr__(self):
        return f"<OrganizationModel (id={self.id}, name={self.name})>"



