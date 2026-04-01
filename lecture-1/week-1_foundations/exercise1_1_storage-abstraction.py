from abc import ABC, abstractmethod
from dataclasses import dataclass
import os
from pathlib import Path

# ============================================================================
# Storage Abstraction 
# ============================================================================
# This interface defines the "Contract" for any storage component. 
# It allows the h business logic to stay decoupled from 
# specific storage technologies.

class Storage(ABC):


    @abstractmethod
    def save(self, key: str, data: bytes) -> bool: 
        pass

    @abstractmethod
    def load(key: str) -> bytes:
        pass

    @abstractmethod
    def delete(key: str) -> bool:
        pass

    @abstractmethod
    def exists(key: str) -> bool:
        pass

# ----------------------------------------------------------------------------
# FileSystem Implementation
# ----------------------------------------------------------------------------
# Implements storage using the local file system.

class FileSystemStorage(Storage):

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save(self, key: str, data: bytes) -> bool:
        try:
            (self.base_path / key).write_bytes(data)
            return True
        except Exception:
            return False

    def load(self, key: str) -> bytes:
        try:
            return (self.base_path / key).read_bytes()
        except FileNotFoundError:
            raise KeyError(f"Key '{key}' not found in file storage.")

    def delete(self, key: str) -> bool:
        try:
            (self.base_path / key).unlink()
            return True
        except FileNotFoundError:
            return False

    def exists(self, key: str) -> bool:
        return (self.base_path / key).exists()
    

# ----------------------------------------------------------------------------
# InMemory Implementation
# ----------------------------------------------------------------------------
# Implements storage using the process's memory.

class InMemoryStorage(Storage):
    def __init__(self):
        self._data: dict[str, bytes] = {}

    def save(self, key: str, data: bytes) -> bool:
        self._data[key] = data
        return True

    def load(self, key: str) -> bytes:
        if key not in self._data:
            raise KeyError(f"Key '{key}' not found in memory.")
        return self._data[key]

    def delete(self, key: str) -> bool:
        return self._data.pop(key, None) is not None

    def exists(self, key: str) -> bool:
        return key in self._data


# ============================================================================
# Document Orchestration
# ============================================================================
# DocumentManager is the "Client" of the Storage abstraction.
# It depends on the 'Storage' interface, not the concrete classes, allowing it to work with any storage implementation.

class DocumentManager:

    """
    Only knows about the 'Storage' interface (through dependency injection).
    It has no idea if it's talking to a the file storage or the memory storage.
    """

    def __init__(self, storage: Storage):
        self.storage = storage

    def save_document(self, name: str, content: str) -> bool:
        return self.storage.save(name, content.encode('utf-8'))
    
    def load_document(self, name: str) -> str:
        return self.storage.load(name).decode('utf-8')
    
if __name__ == "__main__":
    # Using file system storage
    file_storage = FileSystemStorage("documents")
    doc_manager_file = DocumentManager(file_storage)
    doc_manager_file.save_document("example.txt", "Hello, File System!")
    print(doc_manager_file.load_document("example.txt"))

    # Using in-memory storage
    memory_storage = InMemoryStorage()
    doc_manager_memory = DocumentManager(memory_storage)
    doc_manager_memory.save_document("example.txt", "Hello, In-Memory Storage!")
    print(doc_manager_memory.load_document("example.txt"))







        
        

