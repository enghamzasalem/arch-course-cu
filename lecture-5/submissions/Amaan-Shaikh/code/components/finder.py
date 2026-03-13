from typing import List, Optional
from datetime import datetime
from task_models import TaskItem

class ItemFinder:
    """Search and filter tasks."""
    
    def search_by_text(self, items: List[TaskItem], term: str):
        """Search in title and description."""
        term = term.lower()
        results = []
        for item in items:
            if (term in item.title.lower() or 
                term in item.description.lower()):
                results.append(item)
        return results
    
    def filter_items(
        self,
        items: List[TaskItem],
        owner: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[int] = None,
        label: Optional[str] = None
    ):
        """Filter tasks by criteria."""
        result = items
        
        if owner:
            result = [i for i in result if i.owner == owner]
        
        if status:
            result = [i for i in result if i.status.value == status]
        
        if priority:
            result = [i for i in result if i.priority.value == priority]
        
        if label:
            result = [i for i in result if label in i.labels]
        
        return result