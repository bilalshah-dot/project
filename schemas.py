from pydantic import BaseModel

class StudentCreate(BaseModel):
    Name: str
    Reg_ID: str

class StudentResponse(BaseModel):
    Serial_no: int
    Name: str
    Reg_ID: str
    Behavior_Score: int

    class Config:
        from_attributes = True

class StudentUpdate(BaseModel):
    Behavior_Score: int