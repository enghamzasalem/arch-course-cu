from typing import List
from datetime import datetime
from task_models import TaskItem

class TaskAlerter:
    """Sends reminders for upcoming tasks."""
    
    def __init__(self, log_file="alerts.log"):
        self.log_file = log_file
    
    def _log(self, message: str):
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()}: {message}\n")
    
    def check_deadlines(self, items: List[TaskItem], days_ahead: int = 2):
        """Check for tasks due soon."""
        today = datetime.now().date()
        count = 0
        
        for item in items:
            if not item.deadline or item.status.value == "done":
                continue
            
            try:
                deadline = datetime.strptime(item.deadline, "%Y-%m-%d").date()
                days = (deadline - today).days
                
                if 0 <= days <= days_ahead:
                    msg = f"Task '{item.title}' due in {days} days"
                    print(f"🔔 {msg}")
                    self._log(msg)
                    count += 1
            except ValueError:
                continue
        
        return count