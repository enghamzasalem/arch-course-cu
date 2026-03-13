from __future__ import annotations
import abc
from pathlib import Path


class Storage(abc.ABC):
    @abc.abstractmethod
    def save(self, key: str, data: bytes) -> bool:
        pass

    @abc.abstractmethod
    def load(self, key: str) -> bytes:
        pass

    @abc.abstractmethod
    def delete(self, key: str) -> bool:
        pass

    @abc.abstractmethod
    def exists(self, key: str) -> bool:
        pass


class FileSystemStorage(Storage):
    def __init__(self, base_dir: str = "./data"):
        self.base = Path(base_dir)
        self.base.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        return self.base / key

    def save(self, key: str, data: bytes) -> bool:
        p = self._path(key)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)
        return True

    def load(self, key: str) -> bytes:
        p = self._path(key)
        return p.read_bytes()

    def delete(self, key: str) -> bool:
        p = self._path(key)
        if p.exists():
            p.unlink()
            return True
        return False

    def exists(self, key: str) -> bool:
        return self._path(key).exists()


class InMemoryStorage(Storage):
    def __init__(self):
        self._store: dict[str, bytes] = {}

    def save(self, key: str, data: bytes) -> bool:
        self._store[key] = data
        return True

    def load(self, key: str) -> bytes:
        return self._store[key]

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def exists(self, key: str) -> bool:
        return key in self._store


class DocumentManager:
    def __init__(self, storage: Storage):
        self.storage = storage

    def save_document(self, name: str, text: str) -> bool:
        return self.storage.save(name, text.encode("utf-8"))

    def load_document(self, name: str) -> str:
        return self.storage.load(name).decode("utf-8")

    def delete_document(self, name: str) -> bool:
        return self.storage.delete(name)

    def exists(self, name: str) -> bool:
        return self.storage.exists(name)


def _demo_with(storage: Storage) -> None:
    dm = DocumentManager(storage)
    assert not dm.exists("doc1.txt")
    dm.save_document("doc1.txt", "Hello, Architecture!")
    assert dm.exists("doc1.txt")
    assert dm.load_document("doc1.txt") == "Hello, Architecture!"
    dm.delete_document("doc1.txt")
    assert not dm.exists("doc1.txt")


if __name__ == "__main__":
    print("Demo: InMemoryStorage")
    _demo_with(InMemoryStorage())
    print("InMemoryStorage demo passed")

    print("Demo: FileSystemStorage (data/)")
    _demo_with(FileSystemStorage("data"))
    print("FileSystemStorage demo passed")
