import json
import csv


class TaskExporter:
    def export_to_json(self, tasks, filename):
        with open(filename, "w", encoding="utf-8") as file:
            json.dump([task.to_dict() for task in tasks], file, indent=4)

    def export_to_csv(self, tasks, filename):
        if not tasks:
            with open(filename, "w", newline="", encoding="utf-8") as file:
                file.write("")
            return

        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=tasks[0].to_dict().keys())
            writer.writeheader()
            for task in tasks:
                writer.writerow(task.to_dict())
