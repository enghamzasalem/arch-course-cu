from typing import Dict, Optional, List
from task_models import TaskItem, ItemStatus, ItemPriority
from components.storage import IItemStore
from components.verifier import InputVerifier
from components.finder import ItemFinder
from components.formatter import IItemFormatter
from components.alerter import TaskAlerter

class TaskOrchestrator:
    """Main coordinator that receives dependencies via constructor."""
    
    def __init__(
        self,
        storage: IItemStore,           # Depends on interface
        verifier: InputVerifier,
        finder: ItemFinder,
        formatter: IItemFormatter,      # Depends on interface
        alerter: TaskAlerter
    ):
        self.storage = storage
        self.verifier = verifier
        self.finder = finder
        self.formatter = formatter
        self.alerter = alerter
    
    def create_task(self, data: Dict):
        """Create a new task."""
        # Validate
        ok, err = self.verifier.verify_new_item(data)
        if not ok:
            return f"Error: {err}"
        
        # Check if exists
        if self.storage.get_item(data["item_id"]):
            return f"Task {data['item_id']} already exists"
        
        # Create and save
        task = TaskItem.from_dict(data)
        self.storage.add_item(task)
        return f"✓ Task '{task.title}' created"
    
    def update_task(self, task_id: str, updates: Dict):
        """Update existing task."""
        task = self.storage.get_item(task_id)
        if not task:
            return f"Task {task_id} not found"
        
        # Validate updates
        ok, err = self.verifier.verify_changes(updates)
        if not ok:
            return f"Error: {err}"
        
        # Apply updates
        if "title" in updates:
            task.title = updates["title"]
        if "description" in updates:
            task.description = updates["description"]
        if "status" in updates:
            task.status = ItemStatus(updates["status"])
        if "priority" in updates:
            task.priority = ItemPriority(updates["priority"])
        if "owner" in updates:
            task.owner = updates["owner"]
        if "deadline" in updates:
            task.deadline = updates["deadline"]
        if "labels" in updates:
            task.labels = updates["labels"]
        
        self.storage.update_item(task)
        return f"✓ Task {task_id} updated"
    
    def delete_task(self, task_id: str):
        """Remove a task."""
        if self.storage.remove_item(task_id):
            return f"✓ Task {task_id} deleted"
        return f"Task {task_id} not found"
    
    def search(self, keyword: str):
        """Search tasks by text."""
        all_tasks = self.storage.get_all_items()
        return self.finder.search_by_text(all_tasks, keyword)
    
    def filter(self, **kwargs):
        """Filter tasks by criteria."""
        all_tasks = self.storage.get_all_items()
        return self.finder.filter_items(
            all_tasks,
            owner=kwargs.get("owner"),
            status=kwargs.get("status"),
            priority=kwargs.get("priority"),
            label=kwargs.get("label")
        )
    
    def export(self):
        """Export all tasks in current format."""
        all_tasks = self.storage.get_all_items()
        return self.formatter.format_items(all_tasks)
    
    def send_reminders(self):
        """Check and send reminders."""
        all_tasks = self.storage.get_all_items()
        count = self.alerter.check_deadlines(all_tasks)
        return f"{count} reminders sent"