# Task API — Connecting Your CRUD to the Database
> **FlyRank Internship · Backend Track · Week 3 · Assignment A2**  
> Moving from in-memory storage to a production-ready, persistent SQLite database while maintaining 100% backward compatibility with Assignment 1 endpoints.

---

## 1. Overview & Architecture Transition

In Assignment 1, data lived in program memory (Python list variables). Every time the server restarted, all created and updated tasks vanished. In Week 3, the storage layer was replaced with a real, persistent **SQLite database (`tasks.db`)**.

```
Assignment 1:  Client ──> API ──> List in Memory (RAM - lost on restart)
Assignment 2:  Client ──> API ──> SQLite Database (tasks.db on disk - persistent)
```

### Why Identical Tests Passing Proves Storage is "Just an Implementation Detail"
All 33 QC tests from Assignment 1 pass 100% against the new SQLite version without altering the test assertions or client-facing contract. The client sends the exact same requests and receives the exact same response shapes and HTTP status codes (`200`, `201`, `204`, `400`, `404`). The API specifies **what** the application does; the database determines **where and how** it preserves data. Swapping memory for disk is purely an internal architectural change.

---

## 2. Why SQLite?

1. **Zero Configuration & Serverless**: SQLite requires no external daemon, background service, connection credentials, or network configuration.
2. **Single-File Portability**: The entire database lives in a single compact file (`tasks.db`).
3. **Guaranteed Persistence (ACID)**: Data survives application crashes, server restarts, and system reboots.
4. **Standard Library Integration**: Python's native `sqlite3` module ships out of the box with zero third-party dependencies required for the database engine.

### Database Location & Auto-Creation
- **Path**: Located at `W3/tasks.db` (created automatically upon application startup if missing).
- **Git Ignored**: `.gitignore` excludes `tasks.db` so every new clone starts with a clean slate and seeds automatically without committing binary database states.

---

## 3. Quickstart: One Documented Run Command

To clone the repository, create and activate a virtual environment, install dependencies, and launch the server:

```bash
git clone https://github.com/StevenHarun/flyrank-crud-api.git && cd flyrank-crud-api && python -m venv .venv && .\.venv\Scripts\activate && pip install -r requirements.txt && uvicorn main:app --reload --port 8000
```

*(On Linux / macOS, use `source .venv/bin/activate`)*

### Verification on Clean Startup
When the server boots for the first time:
1. `tasks.db` is created automatically.
2. The `tasks` table and indexes (`idx_tasks_done`, `idx_tasks_title`) are provisioned.
3. The table is verified empty (`COUNT(*) == 0`) and seeded with the initial 3 sample tasks atomically inside a transaction.
4. Subsequent restarts check the count and **never duplicate** seed data.

---

## 4. Endpoints Specification Table

| Method | Endpoint | Description | Request Body | Status Codes |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/` | API Root information and available endpoints | None | `200 OK` |
| `GET` | `/health` | Server health check status | None | `200 OK` |
| `GET` | `/tasks` | List all tasks from SQLite (supports `?done=bool`, `?search=str`, `?sort=str`) | None | `200 OK` |
| `GET` | `/tasks/{id}` | Retrieve single task by ID from SQLite (`SELECT ... WHERE id = ?`) | None | `200 OK`, `404 Not Found` |
| `POST` | `/tasks` | Insert new task (`INSERT INTO tasks ...`) with auto ID and `done=false` | `{"title": "string"}` | `201 Created`, `400 Bad Request` |
| `PUT` | `/tasks/{id}` | Update task title and/or done status (`UPDATE tasks SET ... WHERE id = ?`) | `{"title": "str", "done": bool}` | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/tasks/{id}` | Delete task from SQLite (`DELETE FROM tasks WHERE id = ?`) | None | `204 No Content`, `404 Not Found` |
| `GET` | `/stats` | Analytics computed in SQL (`SELECT COUNT(*)`) | None | `200 OK` |
| `POST` | `/reset` | Atomically reset SQLite table back to initial 3 seed tasks | None | `200 OK` |

---

## 5. Database Schema & DB Browser Inspection

### Table Structure: `tasks`
```sql
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    done INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks(done);
CREATE INDEX IF NOT EXISTS idx_tasks_title ON tasks(title);
```

### DB Browser for SQLite Representation
When opening `tasks.db` in **DB Browser for SQLite**:

```
+----+------------------------------------+------+
| id | title                              | done |
+----+------------------------------------+------+
|  1 | Learn HTTP and REST basics         |    1 |
|  2 | Build your first CRUD API          |    0 |
|  3 | Publish project to GitHub          |    0 |
+----+------------------------------------+------+
```

### Stage 4: Executing SQL By Hand
In DB Browser's **Execute SQL** tab (or via `explore_sql.sql`), the following queries were executed and validated against live API behavior:

```sql
-- 1. List every task
SELECT * FROM tasks;

-- 2. List only completed tasks
SELECT * FROM tasks WHERE done = 1;

-- 3. Count total tasks
SELECT COUNT(*) FROM tasks;

-- 4. Mark every task as completed
UPDATE tasks SET done = 1;

-- 5. Delete all completed tasks
DELETE FROM tasks WHERE done = 1;
```

**Checkpoint Reflection**:
> Executing `UPDATE tasks SET done = 1;` in DB Browser immediately changed all `done` values to `true` when calling `GET /tasks` from the API without restarting the server. This proves that both DB Browser and the FastAPI server read from the exact same SQLite database file as the single source of truth.

---

## 6. Extras & Stretch Goals

### 1. Database Indexing
```sql
CREATE INDEX IF NOT EXISTS idx_tasks_done ON tasks(done);
CREATE INDEX IF NOT EXISTS idx_tasks_title ON tasks(title);
```
> **What an index is for**: An index is a specialized lookup data structure (B-Tree in SQLite) that allows the database engine to find matching rows in $O(\log N)$ time rather than performing a full table scan ($O(N)$), drastically speeding up queries with `WHERE done = ?` and `WHERE title = ?`.

### 2. Atomic Database Transactions
Seeding is wrapped in an explicit transaction:
```python
cursor.execute("BEGIN TRANSACTION")
cursor.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", initial_tasks)
conn.commit()
```
> **Why transactions matter**: Wrapping multiple operations in a transaction guarantees atomicity (all-or-nothing). If the application crashes halfway through an insertion, the entire transaction rolls back, preventing corrupt, incomplete, or partially-seeded states.

### 3. Dynamic SQL Search, Filter & Sort
- **Search**: `GET /tasks?search=CRUD` generates `WHERE title LIKE ?` with parameter `f"%{search}%"`.
- **Status Filter**: `GET /tasks?done=true` generates `WHERE done = 1`.
- **Alphabetical Sort**: `GET /tasks?sort=title_asc` executes `ORDER BY title ASC`.

---

## 7. Automated QC Test Suite

Run the full automated test suite (37 tests covering CRUD, HTTP status codes, error payload schemas, restart persistence, indexing, and sorting):

```bash
python test_qc.py
```

### Sample Output:
```
============================================================
      RUNNING AUTOMATED QUALITY CONTROL (QC) TEST SUITE     
============================================================

 [PASS] Stage 1: GET / returns 200 OK
 [PASS] Stage 1: GET / returns expected API metadata
 [PASS] Stage 1: GET /health returns 200 OK
 [PASS] Stage 1: GET /health returns status ok
 [PASS] Stage 2: GET /tasks returns 200 OK
 [PASS] Stage 2: Initial tasks count is 3
 [PASS] Stage 2: GET /tasks/1 returns 200 OK
 [PASS] Stage 2: Task 1 has id=1 and title text
 [PASS] Stage 2: GET /tasks/99 returns 404 Not Found
 [PASS] Stage 2: 404 response body contains 'Task 99 not found'
 [PASS] Stage 3: POST /tasks with valid title returns 201 Created
 [PASS] Stage 3: Created task has new id=4, done=False, title='Buy milk'
 [PASS] Stage 3: Task list now contains 4 items
 [PASS] Stage 3: POST /tasks with empty object returns 400 Bad Request
 [PASS] Stage 3: 400 response body contains error key
 [PASS] Stage 3: POST /tasks with empty string returns 400 Bad Request
 [PASS] Stage 3: POST /tasks with whitespace-only returns 400 Bad Request
 [PASS] Stage 4: PUT /tasks/4 returns 200 OK
 [PASS] Stage 4: PUT /tasks/4 correctly updated title and done=True
 [PASS] Stage 4: PUT /tasks/99 returns 404 Not Found
 [PASS] Stage 4: PUT /tasks/4 with empty body returns 400 Bad Request
 [PASS] Stage 4: DELETE /tasks/4 returns 204 No Content
 [PASS] Stage 4: 204 response body is empty
 [PASS] Stage 4: Confirm deleted task returns 404
 [PASS] Stage 4: DELETE /tasks/99 returns 404 Not Found
 [PASS] Stage 5: GET /docs returns 200 OK (Swagger UI)
 [PASS] Stage 5: Swagger UI contains html payload
 [PASS] Stage 5: GET /openapi.json returns 200 OK
 [PASS] Stage 5: OpenAPI spec defines /tasks paths
 [PASS] Extras: GET /tasks?done=true returns only completed tasks
 [PASS] Extras: GET /tasks?search=CRUD filters tasks by keyword
 [PASS] Extras: GET /stats returns 200 OK with total, done, open counts
 [PASS] Extras: POST /reset restores seed tasks back to 3 items
 [PASS] SQLite: idx_tasks_done index exists in database
 [PASS] SQLite: idx_tasks_title index exists in database
 [PASS] SQLite Extras: GET /tasks?sort=title_asc correctly sorts alphabetically
 [PASS] SQLite: Restarting multiple times does NOT duplicate seeds (count remains 3)

============================================================
   QC COMPLETED SUCCESSFULLY: 37/37 TESTS PASSED (100%)
============================================================
```

---

## 8. Stage 6 Bonus: "AI vs Me" Code Review

As part of the bonus challenge, an AI model was prompted in quarantine (`ai-version/main.py`) to migrate an in-memory CRUD app to SQLite. The code was inspected using `git diff --no-index main.py ai-version/main.py`.

### The Prompt Used
```text
Please migrate this FastAPI task CRUD API from in-memory storage to SQLite using Python's built-in sqlite3 library.
Requirements:
- Database file named 'tasks.db' located in the same directory.
- Create table 'tasks' if missing with columns: id (integer, primary key auto-increment), title (text), done (integer 0 or 1).
- Seed exactly 3 example tasks ('Learn HTTP and REST basics', 'Build your first CRUD API', 'Publish project to GitHub') only when the table is empty; do not re-seed or duplicate on restart.
- Maintain the 5 CRUD endpoints: GET /tasks, GET /tasks/{id}, POST /tasks, PUT /tasks/{id}, DELETE /tasks/{id} plus GET / and GET /health.
- Ensure all SQL queries are parameterized (use ? placeholders) to prevent SQL injection.
- Handle validation: missing/empty title on create should return 400, unknown id on GET/PUT/DELETE should return 404 with JSON error.
- PUT should update title and/or done and return 200; DELETE should return 204 with empty body.
```

### Concrete Differences Identified

1. **Error Response Consistency**:
   - **AI**: Raised `HTTPException(status_code=400, detail="...")` which produced `{"detail": "..."}`.
   - **Handcrafted**: Implemented a centralized exception handler overriding FastAPI's default 422 to always return `400 Bad Request` with `{"error": "..."}` for all validation failures, preserving exact API contracts.
2. **Atomic Seeding & Transactions**:
   - **AI**: Executed multiple separate `cursor.execute()` statements sequentially without an explicit transaction context.
   - **Handcrafted**: Wrapped seeding inside `BEGIN TRANSACTION` ... `COMMIT` using `cursor.executemany()` for batch performance and all-or-nothing atomicity.
3. **Database Indexing & Query Filters**:
   - **AI**: Performed simple unindexed `SELECT * FROM tasks` without supporting status filtering or title search.
   - **Handcrafted**: Created dedicated indexes (`idx_tasks_done`, `idx_tasks_title`) and implemented dynamic parameterized filtering (`WHERE done = ?`, `WHERE title LIKE ?`, `ORDER BY title ASC`).
4. **Empty Body Handling in PUT**:
   - **AI**: Allowed empty bodies `{}` on `PUT /tasks/{id}` without error, silently leaving the record unchanged while returning 200.
   - **Handcrafted**: Validated that at least one field (`title` or `done`) must be present, correctly rejecting empty bodies with `400 Bad Request`.

### Prompt Iteration Lesson
> An AI's output is only as precise as the specification provided. When error payload keys (`{"error": ...}` vs `{"detail": ...}`) and partial update rejection rules are left unspecified, the AI silently defaults to framework conveniences. Building the solution by hand first provides the foundational domain knowledge required to perform rigorous, professional code reviews on AI-generated software.
