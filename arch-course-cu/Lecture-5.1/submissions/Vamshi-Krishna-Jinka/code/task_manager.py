from components.validator import TaskValidator
from components.search import TaskSearch
from components.notifier import TaskNotifier


class TaskManager:

    def __init__(self, repository, exporter):
        self.repository = repository
        self.exporter = exporter

        self.validator = TaskValidator()
        self.search = TaskSearch()
        self.notifier = TaskNotifier()

    def create_task(self, task):

        self.validator.validate(task)
        self.repository.add_task(task)

    def delete_task(self, task_id):

        self.repository.delete_task(task_id)

    def get_tasks(self):

        return self.repository.get_tasks()

    def search_tasks(self, keyword):

        tasks = self.repository.get_tasks()
        return self.search.search_by_title(tasks, keyword)

    def export_tasks(self, filename):

        tasks = self.repository.get_tasks()
        self.exporter.export(tasks, filename)

    def send_reminders(self):

        for task in self.repository.get_tasks():
            self.notifier.send_reminder(task)