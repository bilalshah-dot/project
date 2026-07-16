from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, SessionLocal

# Build the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ENDPOINT 1: View all students
@app.get("/students/", response_model=list[schemas.StudentResponse])
def get_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()

# ENDPOINT 2: Add a new student
@app.post("/students/", response_model=schemas.StudentResponse)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    # Notice the Capital variables here
    new_student = models.Student(Name=student.Name, Reg_ID=student.Reg_ID)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

# ENDPOINT 3: Update a student's behavior score
@app.patch("/students/{Serial_no}", response_model=schemas.StudentResponse)
def update_score(Serial_no: int, score_update: schemas.StudentUpdate, db: Session = Depends(get_db)):
    # Notice the Capital variables here
    student = db.query(models.Student).filter(models.Student.Serial_no == Serial_no).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    student.Behavior_Score = score_update.Behavior_Score
    db.commit()
    db.refresh(student)
    return student