from typing import Dict, Tuple, Optional
from datetime import datetime
from task_models import ItemStatus, ItemPriority

class InputVerifier:
    """Validates task data before processing."""
    
    def verify_new_item(self, data: Dict) -> Tuple[bool, Optional[str]]:
        """Check if new task data is valid."""
        if not data.get("item_id"):
            return False, "Missing item ID"
        
        if not data.get("title"):
            return False, "Title cannot be empty"
        
        if len(data["title"].strip()) < 2:
            return False, "Title too short (min 2 characters)"
        
        if data.get("deadline"):
            try:
                deadline_date = datetime.strptime(data["deadline"], "%Y-%m-%d").date()
                today = datetime.now().date()
                if deadline_date < today:
                    return False, "Deadline cannot be in the past"
            except ValueError:
                return False, "Deadline must be in YYYY-MM-DD format"
        
        return True, None
    
    def verify_changes(self, data: Dict) -> Tuple[bool, Optional[str]]:
        """Check if update data is valid."""
        if "title" in data and len(data["title"].strip()) < 2:
            return False, "Title too short"
        
        if "status" in data:
            valid = [s.value for s in ItemStatus]
            if data["status"] not in valid:
                return False, f"Invalid status. Use: {valid}"
        
        if "priority" in data:
            valid = [p.value for p in ItemPriority]
            if data["priority"] not in valid:
                return False, f"Invalid priority. Use: {valid}"
        
        return True, None