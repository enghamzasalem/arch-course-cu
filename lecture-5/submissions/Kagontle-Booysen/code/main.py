from task_manager import TaskManager


def print_tasks(tasks, heading):
    print(f"\n{heading}")
    for task in tasks:
        print(task.to_dict())


def main():
    manager = TaskManager()

    # Create tasks
    manager.create_task(1, "Write report", "Prepare architecture report", "Seth", "Pending")
    manager.create_task(2, "Fix bug", "Resolve login issue", "Alex", "In Progress")
    manager.create_task(3, "Prepare slides", "Create presentation slides", None, "Pending")

    # Show all tasks
    print_tasks(manager.get_all_tasks(), "All Tasks:")

    # Update task
    manager.update_task(1, status="Completed")

    # Assign task
    manager.assign_task(3, "Maria")

    # Search by title
    print_tasks(manager.search_tasks_by_title("slides"), "Search by Title ('slides'):")

    # Filter by status
    print_tasks(manager.filter_tasks_by_status("Pending"), "Filter by Status ('Pending'):")

    # Filter by assigned user
    print_tasks(manager.filter_tasks_by_user("Maria"), "Filter by Assigned User ('Maria'):")

    # Send reminder
    print("\nReminder Output:")
    manager.send_task_reminder(2)

    # Export tasks
    manager.export_tasks_json("tasks.json")
    manager.export_tasks_csv("tasks.csv")
    print("\nTasks exported to tasks.json and tasks.csv")

    # Delete task
    manager.delete_task(2)
    print_tasks(manager.get_all_tasks(), "Tasks After Deletion:")


if __name__ == "__main__":
    main()
