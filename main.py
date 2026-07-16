from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
import schemas
from database import engine, SessionLocal

# Build the database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# This is a helper function to open and close the database connection
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
    # Create the new student object
    new_student = models.Student(name=student.name)
    # Add it to the database
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    return new_student
# ENDPOINT 3: Update a student's behavior score
@app.patch("/students/{student_id}", response_model=schemas.StudentResponse)
def update_score(student_id: int, score_update: schemas.StudentUpdate, db: Session = Depends(get_db)):
    # Find the specific student
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    
    # If the student doesn't exist, throw an error
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    # Update the score and save to database
    student.behavior_score = score_update.behavior_score
    db.commit()
    db.refresh(student)
    return student