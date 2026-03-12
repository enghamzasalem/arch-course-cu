from typing import Iterable, List, Optional
from .models import Task, TaskPriority, TaskStatus
from .components.interfaces import ITaskExporter, ITaskStorage
from .components.validator import TaskValidator

class TaskManager:
    def __init__(self, storage: ITaskStorage, exporter: ITaskExporter, validator: Optional[TaskValidator] = None) -> None:
        self._storage = storage
        self._exporter = exporter
        self._validator = validator or TaskValidator()

    def create_task(self, task_id: str, title: str, description: str = "", assignee: Optional[str] = None, priority: TaskPriority = TaskPriority.MEDIUM) -> Task:
        ok, err = self._validator.validate_new_task(title=title, description=description, assignee=assignee, priority=priority)
        if not ok:
            raise ValueError(err)
        task = Task(id=task_id, title=title, description=description, assignee=assignee, priority=priority)
        self._storage.add(task)
        return task

    def update_status(self, task_id: str, new_status: TaskStatus) -> Task:
        task = self._get(task_id)
        ok, err = self._validator.validate_status_transition(task.status, new_status)
        if not ok:
            raise ValueError(err)
        task.status = new_status
        self._storage.update(task)
        return task

    def reassign(self, task_id: str, new_assignee: Optional[str]) -> Task:
        task = self._get(task_id)
        task.assignee = new_assignee
        self._storage.update(task)
        return task

    def delete_task(self, task_id: str) -> bool:
        return self._storage.delete(task_id)

    def list_tasks(self) -> List[Task]:
        return self._storage.list_all()

    def search_tasks(self, status: Optional[TaskStatus] = None, assignee: Optional[str] = None, priority: Optional[TaskPriority] = None, text: Optional[str] = None) -> List[Task]:
        tasks = self._storage.list_all()
        if status is not None:
            tasks = [t for t in tasks if t.status == status]
        if assignee is not None:
            tasks = [t for t in tasks if t.assignee == assignee]
        if priority is not None:
            tasks = [t for t in tasks if t.priority == priority]
        if text:
            q = text.lower()
            tasks = [t for t in tasks if q in t.title.lower() or q in t.description.lower()]
        return tasks

    def export_tasks(self, tasks: Iterable[Task], destination: str) -> None:
        self._exporter.export(tasks, destination)

    def send_reminders_for_assignee(self, assignee: str) -> None:
        for t in self._storage.find_by_assignee(assignee):
            if t.status != TaskStatus.DONE:
                print(f"[REMINDER] {t.id} '{t.title}' -> {t.assignee or 'unassigned'} ({t.status.value})")

    def _get(self, task_id: str) -> Task:
        t = self._storage.get(task_id)
        if t is None:
            raise KeyError(f"Task {task_id} not found")
        return t
