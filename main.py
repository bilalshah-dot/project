from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List, Optional

import models
import schemas
from database import engine, SessionLocal

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# --- CORS CONFIGURATION ---
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/evidence_logs", StaticFiles(directory="evidence_logs"), name="evidence_logs")

# --- WEBSOCKET CONNECTION MANAGER ---
# This manages Wahid's live dashboard connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------------------------------------------
# STUDENT MANAGEMENT ENDPOINTS
# -------------------------------------------
@app.get("/students/", response_model=list[schemas.StudentResponse])
def get_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()

@app.post("/students/", response_model=schemas.StudentResponse)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    existing_student = db.query(models.Student).filter(models.Student.Reg_ID == student.Reg_ID).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="A student with this Reg_ID already exists!")
    new_student = models.Student(Name=student.Name, Reg_ID=student.Reg_ID)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

@app.patch("/students/{Serial_no}", response_model=schemas.StudentResponse)
def update_score(Serial_no: int, score_update: schemas.StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.Serial_no == Serial_no).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.Behavior_Score = score_update.Behavior_Score
    db.commit()
    db.refresh(student)
    return student

# -------------------------------------------
# TASK 2.3: LIVE EVENT & ANALYTICS ENDPOINTS
# -------------------------------------------

# WebSocket /ws/live-feed
@app.websocket("/ws/live-feed")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# POST /behavior-log/ (Camera Ingestion & Broadcast)
@app.post("/behavior-log/")
async def create_behavior_log(log: schemas.BehaviorLogCreate, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.Reg_ID == log.Reg_ID).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found in database")

    student.Behavior_Score -= 5 

    # Convert the string timestamp (e.g., "20260720_103015") to a real datetime object
    try:
        parsed_time = datetime.strptime(log.timestamp, "%Y%m%d_%H%M%S")
    except ValueError:
        parsed_time = datetime.utcnow()

    new_log = models.BehaviorLog(
        Reg_ID=student.Reg_ID,
        violation_type=log.violation_type,
        timestamp=parsed_time,
        screenshot_path=log.screenshot_path,
        status="active"
    )

    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    db.refresh(student)

    # Blast the live alert to the dashboard
    alert_payload = {
        "id": new_log.id,
        "Reg_ID": new_log.Reg_ID,
        "violation_type": new_log.violation_type,
        "timestamp": new_log.timestamp.isoformat(),
        "screenshot_path": new_log.screenshot_path,
        "status": new_log.status
    }
    await manager.broadcast(alert_payload)
    
    return {"status": "success", "log_id": new_log.id}

# GET /api/violations (Historical Records)
@app.get("/api/violations", response_model=List[schemas.BehaviorLogResponse])
def get_violations(
    limit: int = 50, 
    violation_type: Optional[str] = None, 
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.BehaviorLog)
    
    if violation_type:
        query = query.filter(models.BehaviorLog.violation_type == violation_type)
    if status:
        query = query.filter(models.BehaviorLog.status == status)
        
    return query.order_by(models.BehaviorLog.timestamp.desc()).limit(limit).all()

# PATCH /api/violations/{log_id}/dismiss
@app.patch("/api/violations/{log_id}/dismiss")
def dismiss_violation(log_id: int, db: Session = Depends(get_db)):
    log_entry = db.query(models.BehaviorLog).filter(models.BehaviorLog.id == log_id).first()
    if not log_entry:
        raise HTTPException(status_code=404, detail="Log not found")
    
    log_entry.status = "dismissed"
    db.commit()
    
    return {"status": "updated", "log_id": log_id, "new_status": "dismissed"}

# GET /api/analytics/summary
@app.get("/api/analytics/summary")
def get_analytics_summary(db: Session = Depends(get_db)):
    today = datetime.utcnow().date()
    # Fetch all logs for today
    logs_today = db.query(models.BehaviorLog).filter(func.date(models.BehaviorLog.timestamp) == today).all()
    
    total_violations = len(logs_today)
    breakdown = {"phone": 0, "sleep": 0, "cheat": 0}
    
    for log in logs_today:
        if log.violation_type in breakdown:
            breakdown[log.violation_type] += 1
            
    # Find most frequent student
    most_frequent = db.query(models.BehaviorLog.Reg_ID, func.count(models.BehaviorLog.id).label('count')) \
        .group_by(models.BehaviorLog.Reg_ID) \
        .order_by(func.count(models.BehaviorLog.id).desc()) \
        .first()
        
    most_frequent_student = most_frequent.Reg_ID if most_frequent else "None"

    return {
        "total_violations_today": total_violations,
        "breakdown": breakdown,
        "most_frequent_student": most_frequent_student
    }