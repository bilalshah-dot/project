from sqlalchemy import Column, Integer, String
from database import Base

class Student(Base):
    __tablename__ = "students"

    Serial_no = Column(Integer, primary_key=True, index=True)
    Name = Column(String, index=True)
    Reg_ID = Column(String, unique=True, index=True)
    Behavior_Score = Column(Integer, default=100)