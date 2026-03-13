from orchestrator import TaskOrchestrator
from components.storage import MemoryItemStore, JsonItemStore, SqliteItemStore
from components.verifier import InputVerifier
from components.finder import ItemFinder
from components.formatter import JsonFormatter, CsvFormatter, YamlFormatter, MarkdownFormatter
from components.alerter import TaskAlerter

def print_tasks(tasks, label):
    print(f"\n{label}:")
    if not tasks:
        print("  No tasks")
        return
    for t in tasks:
        print(f"  - {t.item_id}: {t.title} ({t.owner or 'unassigned'})")

print("=" * 70)
print("DEMO: SWAPPING STORAGE IMPLEMENTATIONS")
print("=" * 70)

# ========== DEMO 1: Same app, different storage ==========
print("\n1. Same TaskOrchestrator works with different storage types:\n")

# Create the same components (except storage)
verifier = InputVerifier()
finder = ItemFinder()
alerter = TaskAlerter()

# Memory storage
memory_store = MemoryItemStore()
app1 = TaskOrchestrator(memory_store, verifier, finder, JsonFormatter(), alerter)
app1.create_task({"item_id": "1", "title": "Memory task", "owner": "Alex"})
print("   ✓ Memory storage: task saved")

# JSON storage
json_store = JsonItemStore("demo_tasks.json")
app2 = TaskOrchestrator(json_store, verifier, finder, JsonFormatter(), alerter)
app2.create_task({"item_id": "1", "title": "JSON task", "owner": "Alex"})
print("   ✓ JSON storage: task saved to file")

# SQLite storage
sqlite_store = SqliteItemStore("demo.db")
app3 = TaskOrchestrator(sqlite_store, verifier, finder, JsonFormatter(), alerter)
app3.create_task({"item_id": "1", "title": "SQLite task", "owner": "Alex"})
print("   ✓ SQLite storage: task saved to database")

print("\n   All three apps work exactly the same way!")
print("   The TaskOrchestrator doesn't know which storage it's using.")


print("\n" + "=" * 70)
print("DEMO: SWAPPING FORMATTER IMPLEMENTATIONS")
print("=" * 70)

# ========== DEMO 2: Same app, different formatters ==========
print("\n2. Same app with different export formats:\n")

# Create app with JSON formatter
app = TaskOrchestrator(
    MemoryItemStore(),
    InputVerifier(),
    ItemFinder(),
    JsonFormatter(),  # Start with JSON
    TaskAlerter()
)

# Add some tasks
app.create_task({"item_id": "101", "title": "Buy groceries", "priority": 2})
app.create_task({"item_id": "102", "title": "Finish report", "priority": 3, "owner": "Alex"})

print("   Tasks added. Now exporting in different formats:\n")

# Export as JSON
json_output = app.export()
print("   JSON format:")
print(f"{json_output[:200]}...")  # Show first 200 chars

# SWAP to CSV formatter
print("\n   🔄 Swapping to CSV formatter...")
app.formatter = CsvFormatter()
csv_output = app.export()
print("   CSV format:")
print(csv_output[:200])

# SWAP to Markdown formatter
print("\n   🔄 Swapping to Markdown formatter...")
app.formatter = MarkdownFormatter()
md_output = app.export()
print("   Markdown format:")
print(md_output[:200])

print("\n   ✓ TaskOrchestrator didn't change - just called formatter.format_items()")


print("\n" + "=" * 70)
print("DEMO: SWAPPING AT RUNTIME")
print("=" * 70)

# ========== DEMO 3: Swapping at runtime ==========
print("\n3. You can even swap implementations while the app runs:\n")

app = TaskOrchestrator(
    MemoryItemStore(),
    InputVerifier(),
    ItemFinder(),
    JsonFormatter(),
    TaskAlerter()
)

app.create_task({"item_id": "201", "title": "Runtime demo task"})

print("   Current format: JSON")
print(f"   {app.export()[:100]}...")

print("\n   🔄 Swapping to YAML formatter...")
app.formatter = YamlFormatter()
print("   Current format: YAML")
print(f"   {app.export()[:100]}...")

print("\n   🔄 Swapping to CSV formatter...")
app.formatter = CsvFormatter()
print("   Current format: CSV")
print(f"   {app.export()[:100]}...")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
✓ Two interfaces defined: IItemStore and IItemFormatter
✓ Multiple implementations per interface:
  - IItemStore: MemoryItemStore, JsonItemStore, SqliteItemStore
  - IItemFormatter: JsonFormatter, CsvFormatter, YamlFormatter, MarkdownFormatter
✓ TaskOrchestrator receives dependencies via constructor
✓ Demonstrated swapping implementations:
  - Same app works with different storage types
  - Same app can export in different formats
  - Implementations can be swapped at runtime
""")