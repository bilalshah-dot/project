from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class Student(Base):
    __tablename__ = "students"
    Serial_no = Column(Integer, primary_key=True, index=True)
    Name = Column(String, index=True)
    Reg_ID = Column(String, unique=True, index=True)
    Behavior_Score = Column(Integer, default=100)

class BehaviorLog(Base):
    __tablename__ = "behavior_logs"
    id = Column(Integer, primary_key=True, index=True)
    
    # Maps from Reg_ID as specified in the blueprint
    Reg_ID = Column(String(50), nullable=False) 
    
    violation_type = Column(String(20), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    screenshot_path = Column(String(255), nullable=False)
    
    # New status column added for the dashboard to track reviewed/dismissed alerts
    status = Column(String(20), default="active")