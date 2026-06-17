# Code Starter Template - Task Management System

This is a **starter template** for the Lecture 5 assignment. Use it as a reference structure.

## Structure

```
code_starter/
├── models.py       # Task data model (provided)
├── components/     # Add your components here
│   ├── __init__.py
│   ├── validator.py
│   ├── repository.py
│   ├── search.py
│   ├── exporter.py
│   └── notifier.py
├── task_manager.py # Main orchestrator (you implement)
└── main.py         # Demo/usage (you implement)
```

## What to Implement

1. **Components** - Create each component with single responsibility
2. **Interfaces** - Define Protocol or ABC for storage, exporter
3. **TaskManager** - Orchestrator that composes components via dependency injection
4. **main.py** - Demo that shows the system in action

## Notes

- Copy this structure to your submission `code/` directory
- Customize and extend as needed
- The models.py is provided; focus on component design
- Keep dependencies minimal (stdlib preferred)

## Running

```bash
# After you implement main.py
python main.py
```
