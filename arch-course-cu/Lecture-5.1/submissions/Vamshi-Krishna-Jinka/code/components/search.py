class TaskSearch:

    def filter_by_user(self, tasks, user):
        return [task for task in tasks if task.assigned_to == user]

    def search_by_title(self, tasks, keyword):
        return [task for task in tasks if keyword.lower() in task.title.lower()]