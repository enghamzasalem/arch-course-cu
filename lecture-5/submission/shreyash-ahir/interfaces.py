"""
interfaces.py - Abstract contracts (interfaces) for the Task Management System.

Using Python's typing.Protocol we define structural interfaces that any
concrete implementation must satisfy.  TaskManager depends only on these
interfaces, never on concrete classes — the key mechanism for low coupling.
"""

from __future__ import annotations

from typing import Protocol, List, Optional, runtime_checkable
from models import Task


@runtime_checkable
class ITaskStorage(Protocol):
    """
    Contract for any component that persists and retrieves tasks.

    Two implementations are provided:
      - InMemoryTaskRepository  (fast, no I/O, good for testing)
      - FileTaskRepository      (persists to a JSON file on disk)

    TaskManager receives an ITaskStorage via its constructor and
    never imports either concrete class.
    """

    def save(self, task: Task) -> None: ...
    def get(self, task_id: str) -> Optional[Task]: ...
    def delete(self, task_id: str) -> bool: ...
    def list_all(self) -> List[Task]: ...


@runtime_checkable
class ITaskExporter(Protocol):
    """
    Contract for any component that serialises tasks to an external format.

    Two implementations are provided:
      - JsonExporter  (produces a .json file)
      - CsvExporter   (produces a .csv file)

    TaskManager receives an ITaskExporter via its constructor, so the
    export format can be changed without touching TaskManager at all.
    """

    def export(self, tasks: List[Task], destination: str) -> str: ...
    """Returns the path/string of the exported content."""
