from sqlalchemy import Column, Integer, String
from app import db 

class testModel(db.Model):
    __tablename__ = 'test_table'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)
    
    def __init__(self, name, description=None):
        self.name = name
        self.description = description
    def __repr__(self):
        return f"<testModel(id={self.id}, name={self.name}, description={self.description})>"

