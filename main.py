from typing import Optional, List
from fastapi import FastAPI, Request, Response, Query, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

app = FastAPI(
    title="Task API",
    description="A simple, fast, and robust in-memory To-Do Task CRUD API built with FastAPI.",
    version="1.0"
)

# Custom validation exception handler to return 400 instead of 422
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    for err in exc.errors():
        msg = err.get("msg", "Invalid request body")
        if "Value error, " in msg:
            msg = msg.replace("Value error, ", "")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": msg}
        )
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": "Invalid request body or missing required fields"}
    )

# Pydantic Schemas for Swagger UI documentation & validation
class TaskSchema(BaseModel):
    id: int = Field(..., description="Unique task identifier", example=1)
    title: str = Field(..., description="Title/description of the task", example="Buy milk")
    done: bool = Field(False, description="Completion status", example=False)

class TaskCreate(BaseModel):
    title: str = Field(..., description="Title of the task", example="Buy milk")

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Title is required and cannot be empty")
        return v.strip()

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Updated task title", example="Buy groceries")
    done: Optional[bool] = Field(None, description="Updated completion status", example=True)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip() if v is not None else None

class StatsSchema(BaseModel):
    total: int = Field(..., description="Total number of tasks", example=3)
    done: int = Field(..., description="Number of completed tasks", example=1)
    open: int = Field(..., description="Number of pending/open tasks", example=2)

# Initial baseline dataset for seed & reset
INITIAL_TASKS = [
    {"id": 1, "title": "Learn HTTP and REST basics", "done": True},
    {"id": 2, "title": "Build your first CRUD API", "done": False},
    {"id": 3, "title": "Publish project to GitHub", "done": False},
]

# In-memory working storage
tasks = [dict(t) for t in INITIAL_TASKS]

@app.get(
    "/",
    summary="API Root Information",
    description="Returns metadata about the API and available entry points.",
    tags=["General"]
)
def get_root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get(
    "/health",
    summary="Health Check",
    description="Checks whether the server is alive and functioning properly.",
    tags=["General"]
)
def get_health():
    return {"status": "ok"}

@app.get(
    "/stats",
    summary="Task Statistics",
    description="Returns calculated metrics: total, completed (done), and pending (open) tasks.",
    response_model=StatsSchema,
    tags=["Analytics"]
)
def get_stats():
    total = len(tasks)
    done_count = sum(1 for t in tasks if t["done"])
    return {
        "total": total,
        "done": done_count,
        "open": total - done_count
    }

@app.post(
    "/reset",
    summary="Reset and Seed Tasks",
    description="Restores the in-memory task list to the initial 3 sample tasks.",
    tags=["Administration"]
)
def reset_tasks():
    global tasks
    tasks = [dict(t) for t in INITIAL_TASKS]
    return {"message": "Tasks successfully reset to initial seed data", "count": len(tasks)}

@app.get(
    "/tasks",
    summary="List all tasks",
    description="Retrieves tasks with optional filtering by status (?done=true/false) and title keyword search (?search=keyword).",
    response_model=List[TaskSchema],
    tags=["Tasks"]
)
def get_tasks(
    done: Optional[bool] = Query(None, description="Filter tasks by completion status (true/false)"),
    search: Optional[str] = Query(None, description="Search tasks by title keyword (case-insensitive)")
):
    result = tasks
    if done is not None:
        result = [t for t in result if t["done"] == done]
    if search:
        search_lower = search.strip().lower()
        result = [t for t in result if search_lower in t["title"].lower()]
    return result

@app.get(
    "/tasks/{task_id}",
    summary="Get a single task by ID",
    description="Retrieves details of a specific task by its numeric ID.",
    response_model=TaskSchema,
    tags=["Tasks"]
)
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": f"Task {task_id} not found"}
    )

@app.post(
    "/tasks",
    summary="Create a new task",
    description="Creates a new task with an automatically generated ID and done=false.",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskSchema,
    tags=["Tasks"]
)
def create_task(task_in: TaskCreate):
    next_id = max([t["id"] for t in tasks], default=0) + 1
    new_task = {
        "id": next_id,
        "title": task_in.title,
        "done": False
    }
    tasks.append(new_task)
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=new_task)

@app.put(
    "/tasks/{task_id}",
    summary="Update an existing task",
    description="Replaces a task's title and/or done status with the provided fields.",
    response_model=TaskSchema,
    tags=["Tasks"]
)
async def update_task(task_id: int, request: Request):
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Task {task_id} not found"}
        )

    try:
        raw_body = await request.json()
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Invalid JSON body"}
        )

    if not isinstance(raw_body, dict) or not raw_body:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Request body must contain 'title' and/or 'done'"}
        )

    try:
        task_in = TaskUpdate(**raw_body)
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Invalid request fields"}
        )

    if task_in.title is None and task_in.done is None:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "Request body must contain 'title' and/or 'done'"}
        )

    if task_in.title is not None:
        task["title"] = task_in.title
    if task_in.done is not None:
        task["done"] = task_in.done

    return task

@app.delete(
    "/tasks/{task_id}",
    summary="Delete a task by ID",
    description="Removes a task from the in-memory store. Returns 204 No Content on success.",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Tasks"]
)
def delete_task(task_id: int):
    global tasks
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": f"Task {task_id} not found"}
        )

    tasks = [t for t in tasks if t["id"] != task_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)
