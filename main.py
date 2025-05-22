from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import List, Optional

# ─── Database Setup ─────────────────────────────────────────────────────────────
DATABASE_URL = "sqlite:///students.db"        # SQLite file in your project folder
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    SQLModel.metadata.create_all(engine)      # Create tables if they don’t exist

# ─── Models ─────────────────────────────────────────────────────────────────────
class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    description: str
    complete: bool = Field(default=False)
    student_id: int = Field(foreign_key="student.id")

# ─── FastAPI App & Startup Event ────────────────────────────────────────────────
app = FastAPI()

@app.on_event("startup")
def on_startup():
    init_db()                                 # Ensure DB and tables are ready

# ─── Dependency to Get DB Session ───────────────────────────────────────────────
def get_session():
    with Session(engine) as session:
        yield session

# ─── Student Endpoints ──────────────────────────────────────────────────────────
@app.post("/students/", response_model=Student)
def create_student(student: Student, session: Session = Depends(get_session)):
    session.add(student)
    session.commit()
    session.refresh(student)
    return student

@app.get("/students/", response_model=List[Student])
def read_students(session: Session = Depends(get_session)):
    return session.exec(select(Student)).all()

@app.get("/students/{student_id}", response_model=Student)
def read_student(student_id: int, session: Session = Depends(get_session)):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.put("/students/{student_id}", response_model=Student)
def update_student(student_id: int, student_data: Student, session: Session = Depends(get_session)):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    student.name = student_data.name
    session.add(student)
    session.commit()
    session.refresh(student)
    return student

@app.delete("/students/{student_id}")
def delete_student(student_id: int, session: Session = Depends(get_session)):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    session.delete(student)
    session.commit()
    return {"ok": True}

# ─── Task Endpoints ─────────────────────────────────────────────────────────────
@app.post("/students/{student_id}/tasks/", response_model=Task)
def create_task_for_student(
    student_id: int, task: Task, session: Session = Depends(get_session)
):
    if not session.get(Student, student_id):
        raise HTTPException(status_code=404, detail="Student not found")
    task.student_id = student_id
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.get("/students/{student_id}/tasks/", response_model=List[Task])
def read_tasks_for_student(student_id: int, session: Session = Depends(get_session)):
    return session.exec(select(Task).where(Task.student_id == student_id)).all()

@app.get("/tasks/{task_id}", response_model=Task)
def read_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_data: Task, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.description = task_data.description
    task.complete = task_data.complete
    session.add(task)
    session.commit()
    session.refresh(task)
    return task

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, session: Session = Depends(get_session)):
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    session.delete(task)
    session.commit()
    return {"ok": True}
