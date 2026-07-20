from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# --- STUDENT SCHEMAS ---
class StudentBase(BaseModel):
    Name: str
    Reg_ID: str

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    Behavior_Score: int

class StudentResponse(StudentBase):
    Serial_no: int
    Behavior_Score: int

    class Config:
        orm_mode = True
        from_attributes = True

# --- BEHAVIOR LOG SCHEMAS ---
class BehaviorLogCreate(BaseModel):
    # The payload from the Vision Engine uses these exact keys
    Reg_ID: str
    violation_type: str
    timestamp: str  
    screenshot_path: str

class BehaviorLogResponse(BaseModel):
    id: int
    Reg_ID: str
    violation_type: str
    timestamp: datetime
    screenshot_path: str
    status: str

    class Config:
        orm_mode = True
        from_attributes = True