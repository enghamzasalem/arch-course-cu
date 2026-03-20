from abc import ABC, abstractmethod


class ITaskStorage(ABC):

    @abstractmethod
    def add_task(self, task):
        pass

    @abstractmethod
    def get_tasks(self):
        pass

    @abstractmethod
    def delete_task(self, task_id):
        pass


class InMemoryTaskRepository(ITaskStorage):

    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def get_tasks(self):
        return self.tasks

    def delete_task(self, task_id):
        self.tasks = [t for t in self.tasks if t.id != task_id]