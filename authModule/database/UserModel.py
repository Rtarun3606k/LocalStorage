from sqlalchemy import Column, Integer, String,Index 
from sqlalchemy import Column, Integer, String,Index 
from datetime import datetime,timezone
from app import db 


class UserModel(db.Model):
    __tablename__ = 'user_table'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    dataOfBirth = Column(String(200), nullable=True)
    passwordHash = Column(String(200), nullable=False)
    email = Column(String(200), nullable=False, unique=True ,index=True) 
    createdAt = Column(String(200), nullable=True, default= lambda: datetime.now(timezone.utc).isoformat()) 
    updatedAt = Column(String(200), nullable=True, onupdate= lambda: datetime.now(timezone.utc).isoformat(),default= lambda: datetime.now(timezone.utc).isoformat())



    def __init__(self, name,email ):
        self.name = name
        self.email = email      
    def __repr__(self):
        return f"<UserModel(id={self.id}, name={self.name}, email={self.email})>"
