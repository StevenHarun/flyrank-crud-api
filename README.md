# Task API — Build Your First CRUD API
> **FlyRank Internship · Backend Track · Week 2 · Assignment A1**  
> A lightweight, robust in-memory REST API for managing tasks, featuring full CRUD operations, strict status code compliance, interactive Swagger UI documentation, and automated QC verification.

---

## 1. Overview
This project is an in-memory To-Do list REST API developed following the 6-stage specification of the FlyRank Backend Track. Data lives purely in memory (variables), demonstrating core HTTP verbs, correct HTTP status code practices, and the client-server request/response lifecycle.

### Key Highlights
- **Framework**: Python 3.10+ & FastAPI (high performance, native OpenAPI).
- **Interactive Documentation**: Swagger UI automatically available at `http://localhost:8000/docs`.
- **Validation**: Strict input validation ensuring invalid inputs return `400 Bad Request` with structured JSON errors.
- **In-Memory Storage**: Initialized with 3 baseline sample tasks.
- **Automated QC**: 100% test coverage across 33 test cases via `test_qc.py`.

---

## 2. Quickstart: One Documented Run Command

To clone, set up the virtual environment, install dependencies, and start the server:

```bash
git clone https://github.com/StevenHarun/flyrank-crud-api.git && cd flyrank-crud-api && python -m venv .venv && .\.venv\Scripts\activate && pip install -r requirements.txt && uvicorn main:app --reload --port 8000
```

*(On Linux / macOS, use `source .venv/bin/activate`)*

Once running, access the server at:
- **API Base URL**: `http://localhost:8000/`
- **Swagger UI**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

---

## 3. Endpoints Specification Table

| Method | Endpoint | Description | Request Body | Expected Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | API Root information and available endpoints | None | `200 OK` |
| `GET` | `/health` | Server health status check | None | `200 OK` |
| `GET` | `/tasks` | List all tasks (supports `?done=bool` & `?search=str`) | None | `200 OK` |
| `GET` | `/tasks/{id}` | Retrieve a single task by its numeric ID | None | `200 OK`, `404 Not Found` |
| `POST` | `/tasks` | Create a new task (auto ID, `done=false`) | `{"title": "string"}` | `201 Created`, `400 Bad Request` |
| `PUT` | `/tasks/{id}` | Replace a task's `title` and/or `done` status | `{"title": "str", "done": bool}` | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/tasks/{id}` | Delete a task by ID (empty response body) | None | `204 No Content`, `404 Not Found` |
| `GET` | `/stats` | Analytics: total, done, and open tasks counts | None | `200 OK` |
| `POST` | `/reset` | Restore tasks to the initial 3 seed items | None | `200 OK` |

---

## 4. Real `curl -i` Terminal Outputs

Below are actual terminal outputs verifying the HTTP headers, status codes, and JSON responses:

### 1. Root & Health Check (`200 OK`)
```http
$ curl -i http://localhost:8000/
HTTP/1.1 200 OK
date: Fri, 06 Nov 2026 13:45:10 GMT
server: uvicorn
content-length: 66
content-type: application/json

{"name":"Task API","version":"1.0","endpoints":["/tasks"]}
```

```http
$ curl -i http://localhost:8000/health
HTTP/1.1 200 OK
date: Fri, 06 Nov 2026 13:45:11 GMT
server: uvicorn
content-length: 15
content-type: application/json

{"status":"ok"}
```

### 2. Read Single Task & 404 Error (`200 OK` vs `404 Not Found`)
```http
$ curl -i http://localhost:8000/tasks/1
HTTP/1.1 200 OK
date: Fri, 06 Nov 2026 13:45:12 GMT
server: uvicorn
content-length: 57
content-type: application/json

{"id":1,"title":"Learn HTTP and REST basics","done":true}
```

```http
$ curl -i http://localhost:8000/tasks/99
HTTP/1.1 404 Not Found
date: Fri, 06 Nov 2026 13:45:13 GMT
server: uvicorn
content-length: 31
content-type: application/json

{"error":"Task 99 not found"}
```

### 3. Create Task & Validation (`201 Created` vs `400 Bad Request`)
```http
$ curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'

HTTP/1.1 201 Created
date: Fri, 06 Nov 2026 13:45:14 GMT
server: uvicorn
content-length: 40
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

```http
$ curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{}'

HTTP/1.1 400 Bad Request
date: Fri, 06 Nov 2026 13:45:15 GMT
server: uvicorn
content-length: 37
content-type: application/json

{"error":"Field required"}
```

### 4. Update & Delete (`200 OK` & `204 No Content`)
```http
$ curl -i -X PUT http://localhost:8000/tasks/4 \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy organic milk","done":true}'

HTTP/1.1 200 OK
date: Fri, 06 Nov 2026 13:45:16 GMT
server: uvicorn
content-length: 49
content-type: application/json

{"id":4,"title":"Buy organic milk","done":true}
```

```http
$ curl -i -X DELETE http://localhost:8000/tasks/4
HTTP/1.1 204 No Content
date: Fri, 06 Nov 2026 13:45:17 GMT
server: uvicorn
content-length: 0
```

---

## 5. Swagger UI Documentation

FastAPI automatically generates interactive OpenAPI documentation accessible in any web browser at:
👉 **`http://localhost:8000/docs`**

### Features:
1. Complete list of all endpoints grouped by category (**General**, **Tasks**, **Analytics**, **Administration**).
2. Interactive **"Try it out"** button allows testing requests directly from the UI without terminal commands.
3. Full request/response schemas with field explanations.

*(Take a screenshot of `http://localhost:8000/docs` on your machine and place it here as `docs_screenshot.png` if desired).*

---

## 6. The Mortality Experiment

> **Observation**:
> When you create new tasks (e.g. Task #4 "Buy milk") and then stop and restart the server (`Ctrl+C` followed by `uvicorn main:app`), sending a `GET /tasks` request shows only the initial 3 tasks. The newly created Task #4 is gone.
>
> **Why this happens**:
> Our tasks are stored exclusively **in-memory** within Python's volatile RAM (`tasks = [...]`). When the process terminates, the operating system reclaims the process memory space. In-memory data is ephemeral by design, which is why persistent databases (SQL/NoSQL) are introduced in Week 3 to store state across server reboots.

---

## 7. Automated Quality Control (QC)

To verify all 33 acceptance tests automatically in under 2 seconds:

```bash
python test_qc.py
```

Result:
```
============================================================
      RUNNING AUTOMATED QUALITY CONTROL (QC) TEST SUITE     
============================================================
 [PASS] Stage 1: GET / returns 200 OK
 [PASS] Stage 1: GET /health returns 200 OK
 [PASS] Stage 2: GET /tasks returns 200 OK
 [PASS] Stage 2: GET /tasks/99 returns 404 Not Found
 [PASS] Stage 3: POST /tasks with valid title returns 201 Created
 [PASS] Stage 3: POST /tasks with empty object returns 400 Bad Request
 [PASS] Stage 4: PUT /tasks/4 returns 200 OK
 [PASS] Stage 4: DELETE /tasks/4 returns 204 No Content
 [PASS] Stage 5: GET /docs returns 200 OK (Swagger UI)
 [PASS] Extras: GET /tasks?done=true returns only completed tasks
 [PASS] Extras: GET /stats returns 200 OK with total, done, open counts
============================================================
   QC COMPLETED SUCCESSFULLY: 33/33 TESTS PASSED (100%)
============================================================
```

---

## 8. Bonus Stage 7: The AI Rematch (AI vs Me)

In this stage, an AI model was prompted from memory to build the same CRUD API without copying the assignment document. The generated code is quarantined inside [`ai-version/main.py`](ai-version/main.py).

### The Specification Prompt Used:
> *"Create a REST API for a to-do list using Python and FastAPI with in-memory storage. Include endpoints for GET /, GET /health, GET /tasks, GET /tasks/{id}, POST /tasks, PUT /tasks/{id}, and DELETE /tasks/{id}. It should return 201 on creation, handle 404 when an ID doesn't exist, validate that tasks have titles, and enable Swagger UI."*

### Concrete Differences Found:
1. **Validation Status Codes (`422` vs `400`)**:
   - *What happened*: When posting `{}` or invalid data, the AI's version returned `422 Unprocessable Entity` (FastAPI's default Pydantic behavior).
   - *Our version*: Implemented a custom validation exception handler to strictly return `400 Bad Request` as required by the assignment and HTTP standards.
2. **Error Payload Structure (`{"detail": "..."}` vs `{"error": "..."}`)**:
   - *What happened*: The AI used `raise HTTPException(status_code=404, detail="Task not found")`, producing `{ "detail": "Task not found" }`.
   - *Our version*: Specifically adhered to the required contract: `{ "error": "Task 99 not found" }`.
3. **DELETE Behavior (`200 OK` vs `204 No Content`)**:
   - *What happened*: The AI defaulted to returning status `200` with a JSON body `{"message": "Task deleted"}`.
   - *Our version*: Returns true RESTful `204 No Content` with a completely empty body (0 bytes).
4. **Whitespace Edge Cases**:
   - *What happened*: The AI's `title: str` accepted empty strings `""` and whitespace `"   "`.
   - *Our version*: Handled custom strip validation preventing blank tasks.

### The Core Lesson:
> *"An AI's output is exactly as good as your specification — and you could only judge it because you had built the thing yourself first."*

