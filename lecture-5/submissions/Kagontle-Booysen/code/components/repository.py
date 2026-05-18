class TaskRepository:
    def __init__(self):
        self._tasks = {}

    def add(self, task):
        if task.task_id in self._tasks:
            raise ValueError(f"Task with id {task.task_id} already exists.")
        self._tasks[task.task_id] = task

    def get_by_id(self, task_id):
        return self._tasks.get(task_id)

    def get_all(self):
        return list(self._tasks.values())

    def update(self, task):
        if task.task_id not in self._tasks:
            raise ValueError(f"Task with id {task.task_id} does not exist.")
        self._tasks[task.task_id] = task

    def delete(self, task_id):
        if task_id not in self._tasks:
            raise ValueError(f"Task with id {task_id} does not exist.")
        del self._tasks[task_id]
