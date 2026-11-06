"""
Automated Quality Control (QC) Test Suite
FlyRank Internship - Backend Track - Week 2 Assignment A1: Build your first CRUD API

Run this script directly:
    python test_qc.py
"""

import sys
from fastapi.testclient import TestClient
from main import app, INITIAL_TASKS, reset_tasks

# ANSI Color codes for clean terminal output
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

client = TestClient(app)

tests_run = 0
tests_passed = 0

def check(name: str, condition: bool, details: str = ""):
    global tests_run, tests_passed
    tests_run += 1
    if condition:
        tests_passed += 1
        print(f" {GREEN}[PASS]{RESET} {name}")
    else:
        print(f" {RED}[FAIL]{RESET} {name} -> {details}")

print(f"\n{BLUE}============================================================{RESET}")
print(f"{BLUE}      RUNNING AUTOMATED QUALITY CONTROL (QC) TEST SUITE     {RESET}")
print(f"{BLUE}============================================================{RESET}\n")

# Reset data state first
reset_tasks()

# --- STAGE 1: Root & Health ---
r = client.get("/")
check("Stage 1: GET / returns 200 OK", r.status_code == 200, f"Got {r.status_code}")
check(
    "Stage 1: GET / returns expected API metadata",
    r.json() == {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]},
    str(r.json())
)

r = client.get("/health")
check("Stage 1: GET /health returns 200 OK", r.status_code == 200, f"Got {r.status_code}")
check("Stage 1: GET /health returns status ok", r.json() == {"status": "ok"}, str(r.json()))

# --- STAGE 2: Read Endpoints ---
r = client.get("/tasks")
check("Stage 2: GET /tasks returns 200 OK", r.status_code == 200, f"Got {r.status_code}")
check("Stage 2: Initial tasks count is 3", len(r.json()) == 3, f"Got {len(r.json())}")

r = client.get("/tasks/1")
check("Stage 2: GET /tasks/1 returns 200 OK", r.status_code == 200, f"Got {r.status_code}")
check("Stage 2: Task 1 has id=1 and title text", r.json().get("id") == 1 and isinstance(r.json().get("title"), str))

r = client.get("/tasks/99")
check("Stage 2: GET /tasks/99 returns 404 Not Found", r.status_code == 404, f"Got {r.status_code}")
check("Stage 2: 404 response body contains 'Task 99 not found'", r.json().get("error") == "Task 99 not found", str(r.json()))

# --- STAGE 3: Create Endpoints & Validation ---
r = client.post("/tasks", json={"title": "Buy milk"})
check("Stage 3: POST /tasks with valid title returns 201 Created", r.status_code == 201, f"Got {r.status_code}")
new_task = r.json()
check("Stage 3: Created task has new id=4, done=False, title='Buy milk'",
      new_task.get("id") == 4 and new_task.get("done") is False and new_task.get("title") == "Buy milk")

r_after_post = client.get("/tasks")
check("Stage 3: Task list now contains 4 items", len(r_after_post.json()) == 4)

r = client.post("/tasks", json={})
check("Stage 3: POST /tasks with empty object returns 400 Bad Request", r.status_code == 400, f"Got {r.status_code}")
check("Stage 3: 400 response body contains error key", "error" in r.json())

r = client.post("/tasks", json={"title": ""})
check("Stage 3: POST /tasks with empty string returns 400 Bad Request", r.status_code == 400, f"Got {r.status_code}")

r = client.post("/tasks", json={"title": "   "})
check("Stage 3: POST /tasks with whitespace-only returns 400 Bad Request", r.status_code == 400, f"Got {r.status_code}")

# --- STAGE 4: Update & Delete ---
r = client.put("/tasks/4", json={"title": "Buy organic milk", "done": True})
check("Stage 4: PUT /tasks/4 returns 200 OK", r.status_code == 200, f"Got {r.status_code}")
check("Stage 4: PUT /tasks/4 correctly updated title and done=True",
      r.json().get("title") == "Buy organic milk" and r.json().get("done") is True)

r = client.put("/tasks/99", json={"title": "Non-existent"})
check("Stage 4: PUT /tasks/99 returns 404 Not Found", r.status_code == 404, f"Got {r.status_code}")

r = client.put("/tasks/4", json={})
check("Stage 4: PUT /tasks/4 with empty body returns 400 Bad Request", r.status_code == 400, f"Got {r.status_code}")

r = client.delete("/tasks/4")
check("Stage 4: DELETE /tasks/4 returns 204 No Content", r.status_code == 204, f"Got {r.status_code}")
check("Stage 4: 204 response body is empty", len(r.text) == 0, f"Got text: '{r.text}'")

r = client.get("/tasks/4")
check("Stage 4: Confirm deleted task returns 404", r.status_code == 404, f"Got {r.status_code}")

r = client.delete("/tasks/99")
check("Stage 4: DELETE /tasks/99 returns 404 Not Found", r.status_code == 404, f"Got {r.status_code}")

# --- STAGE 5: Swagger UI & OpenAPI Docs ---
r = client.get("/docs")
check("Stage 5: GET /docs returns 200 OK (Swagger UI)", r.status_code == 200, f"Got {r.status_code}")
check("Stage 5: Swagger UI contains html payload", "swagger-ui" in r.text.lower())

r = client.get("/openapi.json")
check("Stage 5: GET /openapi.json returns 200 OK", r.status_code == 200, f"Got {r.status_code}")
check("Stage 5: OpenAPI spec defines /tasks paths", "/tasks" in r.json().get("paths", {}))

# --- EXTRAS: Filter, Search, Stats, Reset ---
r = client.get("/tasks?done=true")
check("Extras: GET /tasks?done=true returns only completed tasks",
      r.status_code == 200 and all(t["done"] is True for t in r.json()))

r = client.get("/tasks?search=CRUD")
check("Extras: GET /tasks?search=CRUD filters tasks by keyword",
      r.status_code == 200 and len(r.json()) >= 1 and "CRUD" in r.json()[0]["title"])

r = client.get("/stats")
check("Extras: GET /stats returns 200 OK with total, done, open counts",
      r.status_code == 200 and "total" in r.json() and "done" in r.json() and "open" in r.json())

r = client.post("/reset")
check("Extras: POST /reset restores seed tasks back to 3 items",
      r.status_code == 200 and r.json().get("count") == 3)

# Summary
print(f"\n{BLUE}============================================================{RESET}")
if tests_passed == tests_run:
    print(f"{GREEN}   QC COMPLETED SUCCESSFULLY: {tests_passed}/{tests_run} TESTS PASSED (100%){RESET}")
else:
    print(f"{RED}   QC FAILED: {tests_passed}/{tests_run} TESTS PASSED{RESET}")
print(f"{BLUE}============================================================{RESET}\n")

if tests_passed < tests_run:
    sys.exit(1)
