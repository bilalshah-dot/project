from pydantic import BaseModel

class StudentCreate(BaseModel):
    name: str

class StudentResponse(BaseModel):
    id: int
    name: str
    behavior_score: int

    class Config:
        from_attributes = True

class StudentUpdate(BaseModel):
    behavior_score: int