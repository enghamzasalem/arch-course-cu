from typing import Protocol

class ILogger(Protocol):
    def log(self, message: str) -> None: ...

class ConsoleLogger:
    def log(self, message: str) -> None:
        print(f"[LOG]: {message}")

class FileLogger:
    def log(self, message: str) -> None:
        with open("system.log", "a") as f:
            f.write(f"[LOG]: {message}\n")