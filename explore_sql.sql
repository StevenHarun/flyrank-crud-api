-- Stage 4: Learn your first SQL by hand
-- Run these queries directly against tasks.db in DB Browser for SQLite or sqlite3 CLI:

-- 1. List every task
SELECT * FROM tasks;

-- 2. Only completed tasks
SELECT * FROM tasks WHERE done = 1;

-- 3. How many tasks are there?
SELECT COUNT(*) FROM tasks;

-- 4. Mark every task completed
UPDATE tasks SET done = 1;

-- 5. Delete all completed tasks
DELETE FROM tasks WHERE done = 1;
