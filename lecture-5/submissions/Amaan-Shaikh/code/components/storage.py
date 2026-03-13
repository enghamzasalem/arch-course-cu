import json
import sqlite3
import os
from typing import Dict, List, Optional, Protocol
from task_models import TaskItem

# ========== INTERFACE ==========
class IItemStore(Protocol):
    """Interface for task storage operations."""
    
    def add_item(self, item: TaskItem) -> None:
        """Store a new task."""
        pass
    
    def get_item(self, item_id: str) -> Optional[TaskItem]:
        """Retrieve a task by ID."""
        pass
    
    def get_all_items(self) -> List[TaskItem]:
        """Get all stored tasks."""
        pass
    
    def update_item(self, item: TaskItem) -> None:
        """Update an existing task."""
        pass
    
    def remove_item(self, item_id: str) -> bool:
        """Delete a task by ID. Returns True if deleted."""
        pass


# ========== IMPLEMENTATION 1: In-Memory ==========
class MemoryItemStore:
    """Stores tasks in memory (data lost when program ends)."""
    
    def __init__(self):
        self._items: Dict[str, TaskItem] = {}
    
    def add_item(self, item: TaskItem):
        self._items[item.item_id] = item
    
    def get_item(self, item_id: str):
        return self._items.get(item_id)
    
    def get_all_items(self):
        return list(self._items.values())
    
    def update_item(self, item: TaskItem):
        self._items[item.item_id] = item
    
    def remove_item(self, item_id: str):
        if item_id in self._items:
            del self._items[item_id]
            return True
        return False


# ========== IMPLEMENTATION 2: JSON File ==========
class JsonItemStore:
    """Stores tasks in a JSON file."""
    
    def __init__(self, file_path="tasks.json"):
        self.file_path = file_path
        self._ensure_file()
    
    def _ensure_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump([], f)
    
    def _read_items(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [TaskItem.from_dict(x) for x in data]
    
    def _write_items(self, items):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump([i.to_dict() for i in items], f, indent=2)
    
    def add_item(self, item: TaskItem):
        items = self._read_items()
        items.append(item)
        self._write_items(items)
    
    def get_item(self, item_id: str):
        items = self._read_items()
        for i in items:
            if i.item_id == item_id:
                return i
        return None
    
    def get_all_items(self):
        return self._read_items()
    
    def update_item(self, item: TaskItem):
        items = self._read_items()
        for idx, i in enumerate(items):
            if i.item_id == item.item_id:
                items[idx] = item
                break
        self._write_items(items)
    
    def remove_item(self, item_id: str):
        items = self._read_items()
        new_items = [i for i in items if i.item_id != item_id]
        if len(new_items) == len(items):
            return False
        self._write_items(new_items)
        return True


# ========== IMPLEMENTATION 3: SQLite ==========
class SqliteItemStore:
    """Stores tasks in SQLite database."""
    
    def __init__(self, db_path="tasks.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    item_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    status TEXT,
                    priority INTEGER,
                    owner TEXT,
                    deadline TEXT,
                    labels TEXT,
                    created_at TEXT
                )
            """)
    
    def _item_to_row(self, item):
        return (
            item.item_id,
            item.title,
            item.description,
            item.status.value,
            item.priority.value,
            item.owner,
            item.deadline,
            ",".join(item.labels),
            item.created_at.isoformat()
        )
    
    def _row_to_item(self, row):
        data = {
            "item_id": row[0],
            "title": row[1],
            "description": row[2],
            "status": row[3],
            "priority": row[4],
            "owner": row[5],
            "deadline": row[6],
            "labels": row[7].split(",") if row[7] else [],
            "created_at": row[8]
        }
        return TaskItem.from_dict(data)
    
    def add_item(self, item: TaskItem):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO tasks VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                self._item_to_row(item)
            )
    
    def get_item(self, item_id: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM tasks WHERE item_id = ?", 
                (item_id,)
            )
            row = cursor.fetchone()
            return self._row_to_item(row) if row else None
    
    def get_all_items(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM tasks")
            rows = cursor.fetchall()
            return [self._row_to_item(row) for row in rows]
    
    def update_item(self, item: TaskItem):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE tasks 
                SET title=?, description=?, status=?, priority=?, 
                    owner=?, deadline=?, labels=?, created_at=?
                WHERE item_id = ?
            """, (
                item.title, item.description, item.status.value, 
                item.priority.value, item.owner, item.deadline,
                ",".join(item.labels), item.created_at.isoformat(),
                item.item_id
            ))
    
    def remove_item(self, item_id: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "DELETE FROM tasks WHERE item_id = ?", 
                (item_id,)
            )
            return cursor.rowcount > 0