import json
import csv
from typing import List, Protocol
from task_models import TaskItem

# ========== INTERFACE ==========
class IItemFormatter(Protocol):
    """Interface for task formatting/export."""
    
    def format_items(self, items: List[TaskItem]) -> str:
        """Convert tasks to a specific format."""
        pass


# ========== IMPLEMENTATION 1: JSON ==========
class JsonFormatter:
    """JSON format exporter."""
    
    def format_items(self, items):
        data = [i.to_dict() for i in items]
        return json.dumps(data, indent=2)


# ========== IMPLEMENTATION 2: CSV ==========
class CsvFormatter:
    """CSV format exporter."""
    
    def format_items(self, items):
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(["item_id", "title", "status", "priority", 
                        "owner", "deadline", "labels"])
        
        for t in items:
            labels = "|".join(t.labels) if t.labels else ""
            writer.writerow([
                t.item_id, t.title, t.status.value, t.priority.value,
                t.owner or "", t.deadline or "", labels
            ])
        
        return output.getvalue()


# ========== IMPLEMENTATION 3: YAML ==========
# Note: Requires 'pip install pyyaml'
try:
    import yaml
    
    class YamlFormatter:
        """YAML format exporter."""
        
        def format_items(self, items):
            data = [i.to_dict() for i in items]
            return yaml.dump(data, default_flow_style=False, allow_unicode=True)
            
except ImportError:
    # Fallback if yaml not installed
    class YamlFormatter:
        def format_items(self, items):
            return "YAML formatter requires pyyaml. Run: pip install pyyaml"


# ========== IMPLEMENTATION 4: Markdown ==========
class MarkdownFormatter:
    """Markdown table exporter."""
    
    def format_items(self, items):
        if not items:
            return "No tasks found"
        
        lines = []
        lines.append("# Task List\n")
        lines.append("| ID | Title | Status | Priority | Owner | Deadline |")
        lines.append("|-----|-------|--------|----------|-------|----------|")
        
        for t in items:
            lines.append(
                f"| {t.item_id} | {t.title} | {t.status.value} | "
                f"{t.priority.value} | {t.owner or '-'} | "
                f"{t.deadline or '-'} |"
            )
        
        return "\n".join(lines)