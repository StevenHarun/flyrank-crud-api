"""
AI-Generated Task API (Week 3 SQLite Migration - Quarantine Version)
Prompt given:
"Please migrate this FastAPI task CRUD API from in-memory storage to SQLite using Python's built-in sqlite3 library.
Requirements:
- Database file named 'tasks.db' located in the same directory.
- Create table 'tasks' if missing with columns: id (integer, primary key auto-increment), title (text), done (integer 0 or 1).
- Seed exactly 3 example tasks ('Learn HTTP and REST basics', 'Build your first CRUD API', 'Publish project to GitHub') only when the table is empty; do not re-seed or duplicate on restart.
- Maintain the 5 CRUD endpoints: GET /tasks, GET /tasks/{id}, POST /tasks, PUT /tasks/{id}, DELETE /tasks/{id} plus GET / and GET /health.
- Ensure all SQL queries are parameterized (use ? placeholders) to prevent SQL injection.
- Handle validation: missing/empty title on create should return 400, unknown id on GET/PUT/DELETE should return 404 with JSON error.
- PUT should update title and/or done and return 200; DELETE should return 204 with empty body."
"""

import sqlite3
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

DB_FILE = Path(__file__).parent / "tasks.db"

app = FastAPI(title="AI Task API (SQLite)")

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]
    if count == 0:
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Learn HTTP and REST basics", 1))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Build your first CRUD API", 0))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Publish project to GitHub", 0))
        conn.commit()
    conn.close()

init_db()

class Task(BaseModel):
    id: int
    title: str
    done: bool

class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None

@app.get("/")
def read_root():
    return {"message": "Welcome to Task API"}

@app.get("/health")
def read_health():
    return {"status": "ok"}

@app.get("/tasks")
def read_tasks():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    return [{"id": r["id"], "title": r["title"], "done": bool(r["done"])} for r in rows]

@app.get("/tasks/{task_id}")
def read_task(task_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    if not task.title or not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (task.title.strip(), 0))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return {"id": task_id, "title": task.title.strip(), "done": False}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    existing = cursor.fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    new_title = task.title.strip() if task.title is not None else existing["title"]
    new_done = int(task.done) if task.done is not None else existing["done"]

    cursor.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (new_title, new_done, task_id))
    conn.commit()
    conn.close()
    return {"id": task_id, "title": new_title, "done": bool(new_done)}

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return None
