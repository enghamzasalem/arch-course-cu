from abc import ABC, abstractmethod
import json
import csv


class ITaskExporter(ABC):

    @abstractmethod
    def export(self, tasks, filename):
        pass


class JsonExporter(ITaskExporter):

    def export(self, tasks, filename):
        data = [task.__dict__ for task in tasks]

        with open(filename, "w") as f:
            json.dump(data, f, indent=4)


class CsvExporter(ITaskExporter):

    def export(self, tasks, filename):
        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["id", "title", "description", "assigned_to", "status"]
            )

            writer.writeheader()

            for task in tasks:
                writer.writerow(task.__dict__)