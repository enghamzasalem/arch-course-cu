class TaskSearch:
    def search_by_title(self, tasks, keyword):
        keyword = keyword.lower()
        return [task for task in tasks if keyword in task.title.lower()]

    def filter_by_status(self, tasks, status):
        return [task for task in tasks if task.status == status]

    def filter_by_assigned_user(self, tasks, username):
        return [task for task in tasks if task.assigned_to == username]
