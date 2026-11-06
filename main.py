from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Task API", version="1.0")

# In-memory storage with 3 initial example tasks
tasks = [
    {"id": 1, "title": "Learn HTTP and REST basics", "done": True},
    {"id": 2, "title": "Build your first CRUD API", "done": False},
    {"id": 3, "title": "Publish project to GitHub", "done": False},
]

@app.get("/")
def get_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def get_health():
    return {"status": "ok"}

@app.get("/tasks")
def get_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )
