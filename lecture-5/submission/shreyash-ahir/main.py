"""
main.py - Runnable demonstration of the Task Management System.

Shows all required features:
  - Create / update / delete tasks
  - Assign tasks to users
  - Filter and search
  - Export to JSON and CSV
  - Send reminders

Also demonstrates interface swappability:
  The SAME TaskManager instance is reused with a different exporter to
  show that swapping JsonExporter for CsvExporter requires no changes
  to TaskManager.
"""

import sys
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta

from task_manager import TaskManager
from models import TaskStatus, TaskPriority
from components.repository import InMemoryTaskRepository, FileTaskRepository
from components.exporter import JsonExporter, CsvExporter
from components.validator import TaskValidator
from components.search import TaskSearch
from components.notifier import TaskNotifier

SEP = "-" * 60


def section(title: str) -> None:
    print(f"\n{SEP}\n  {title}\n{SEP}")


# ---------------------------------------------------------------------------
# 1.  Wire up the system using InMemoryTaskRepository + JsonExporter
# ---------------------------------------------------------------------------

section("1. Setup — InMemoryTaskRepository + JsonExporter (constructor DI)")

manager = TaskManager(
    storage=InMemoryTaskRepository(),
    exporter=JsonExporter(),
    validator=TaskValidator(),
    searcher=TaskSearch(),
    notifier=TaskNotifier(warning_hours=48),
)

# ---------------------------------------------------------------------------
# 2.  Users
# ---------------------------------------------------------------------------

section("2. Add users")
alice = manager.add_user("Alice", "alice@example.com")
bob   = manager.add_user("Bob",   "bob@example.com")
print(f"  Added: {alice.name} ({alice.user_id[:8]}…)")
print(f"  Added: {bob.name}  ({bob.user_id[:8]}…)")

# ---------------------------------------------------------------------------
# 3.  Create tasks
# ---------------------------------------------------------------------------

section("3. Create tasks")

t1 = manager.create_task(
    "Write unit tests",
    description="Cover validator and search components",
    priority=TaskPriority.HIGH,
    due_date=datetime.utcnow() + timedelta(hours=10),
    tags=["testing", "quality"],
)
t2 = manager.create_task(
    "Update documentation",
    description="Add README and inline comments",
    priority=TaskPriority.MEDIUM,
    due_date=datetime.utcnow() + timedelta(days=5),
    tags=["docs"],
)
t3 = manager.create_task(
    "Deploy to staging",
    description="Run the CI pipeline and push to staging",
    priority=TaskPriority.LOW,
    tags=["devops"],
)
print(f"  Created: '{t1.title}' (id={t1.task_id[:8]}…)")
print(f"  Created: '{t2.title}' (id={t2.task_id[:8]}…)")
print(f"  Created: '{t3.title}' (id={t3.task_id[:8]}…)")

# ---------------------------------------------------------------------------
# 4.  Update a task
# ---------------------------------------------------------------------------

section("4. Update a task")
manager.update_task(t1.task_id, status=TaskStatus.IN_PROGRESS)
updated = manager.get_task(t1.task_id)
print(f"  '{updated.title}' status → {updated.status.value}")

# ---------------------------------------------------------------------------
# 5.  Assign tasks to users
# ---------------------------------------------------------------------------

section("5. Assign tasks")
manager.assign_task(t1.task_id, alice.user_id)
manager.assign_task(t2.task_id, bob.user_id)

# ---------------------------------------------------------------------------
# 6.  Filter and search
# ---------------------------------------------------------------------------

section("6. Filter and search")

in_progress = manager.filter_by_status(TaskStatus.IN_PROGRESS)
print(f"  IN_PROGRESS tasks: {[t.title for t in in_progress]}")

high = manager.filter_by_priority(TaskPriority.HIGH)
print(f"  HIGH priority tasks: {[t.title for t in high]}")

results = manager.search("documentation")
print(f"  Search 'documentation': {[t.title for t in results]}")

# ---------------------------------------------------------------------------
# 7.  Send reminders
# ---------------------------------------------------------------------------

section("7. Send reminders (tasks due within 48 h)")
manager.send_reminders()

# ---------------------------------------------------------------------------
# 8.  Export to JSON
# ---------------------------------------------------------------------------

section("8. Export to JSON (JsonExporter)")
json_path = manager.export_tasks("tasks_export.json")
print(f"  Exported to: {json_path}")

# ---------------------------------------------------------------------------
# 9.  Swap exporter — no changes to TaskManager needed
# ---------------------------------------------------------------------------

section("9. Swap to CsvExporter — same TaskManager, different exporter")
manager_csv = TaskManager(
    storage=InMemoryTaskRepository(),   # fresh storage for demo clarity
    exporter=CsvExporter(),             # <-- only this line changed
    validator=TaskValidator(),
    searcher=TaskSearch(),
    notifier=TaskNotifier(),
)
# Repopulate with same tasks for demo
for task in [t1, t2, t3]:
    manager_csv._storage.save(task)

csv_path = manager_csv.export_tasks("tasks_export.csv")
print(f"  Exported to: {csv_path}")

# ---------------------------------------------------------------------------
# 10.  Delete a task
# ---------------------------------------------------------------------------

section("10. Delete a task")
deleted = manager.delete_task(t3.task_id)
print(f"  Deleted '{t3.title}': {deleted}")
remaining = manager.list_tasks()
print(f"  Remaining tasks: {[t.title for t in remaining]}")

# ---------------------------------------------------------------------------
# 11.  Demonstrate FileTaskRepository swap
# ---------------------------------------------------------------------------

section("11. Swap storage — FileTaskRepository (same interface, no code change in TaskManager)")
file_manager = TaskManager(
    storage=FileTaskRepository("tasks_file_repo.json"),  # <-- different storage
    exporter=JsonExporter(),
)
ft = file_manager.create_task(
    "Persisted task",
    description="This task is saved to disk",
    priority=TaskPriority.HIGH,
)
print(f"  Created and persisted: '{ft.title}' → tasks_file_repo.json")
retrieved = file_manager.get_task(ft.task_id)
print(f"  Retrieved from file:   '{retrieved.title}' (status={retrieved.status.value})")

# Cleanup demo files
for f in ["tasks_export.json", "tasks_export.csv", "tasks_file_repo.json"]:
    if os.path.exists(f):
        os.remove(f)

section("Done — all features demonstrated.")
