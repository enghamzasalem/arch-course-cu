#!/usr/bin/env python3
"""
Exercise 1.1: Create a Storage Abstraction 🟢

This example demonstrates:
- How abstraction hides storage implementation complexity
- Interface design principles for storage backends
- Information hiding in data persistence
- Real-world business scenario: Document Management System

Key Concept: Abstraction allows us to work with different storage systems
by hiding implementation details and exposing only what's necessary.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime
import os
import shutil
import json


# ============================================================================
# BUSINESS SCENARIO: Document Management System
# ============================================================================
# Imagine you're building a document management platform. You need to support
# multiple storage backends (local disk, cloud storage, database) without
# coupling your document workflows to any specific implementation.
# This is where abstraction shines!


@dataclass
class Document:
    """Document metadata and content"""
    id: str
    name: str
    content: bytes
    created_at: datetime
    updated_at: datetime
    size: int
    mime_type: str


@dataclass
class StorageResult:
    """Result of a storage operation"""
    success: bool
    key: Optional[str] = None
    message: Optional[str] = None
    document: Optional[Document] = None


# ============================================================================
# ABSTRACTION: Storage Interface
# ============================================================================
# This interface defines WHAT a storage backend can do, not HOW it does it.
# Any storage implementation must provide these methods, but the implementation
# details are hidden.

class Storage(ABC):
    """
    Abstract interface for storage backends.
    
    This is the ARCHITECTURAL CONTRACT - it defines the behavior that all
    storage systems must provide, regardless of their implementation.
    
    Key Principle: Clients depend on the interface, not the implementation.
    This allows us to swap storage backends without changing client code.
    """
    
    @abstractmethod
    def save(self, key: str, data: bytes) -> StorageResult:
        """
        Save data under the given key.
        
        Args:
            key: Unique identifier for the data
            data: Binary data to store
            
        Returns:
            StorageResult with operation status
        """
        pass
    
    @abstractmethod
    def load(self, key: str) -> StorageResult:
        """
        Load data for the given key.
        
        Args:
            key: Unique identifier for the data
            
        Returns:
            StorageResult with data if successful
        """
        pass
    
    @abstractmethod
    def delete(self, key: str) -> StorageResult:
        """
        Delete data for the given key.
        
        Args:
            key: Unique identifier for the data
            
        Returns:
            StorageResult with operation status
        """
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """
        Check if data exists for the given key.
        
        Args:
            key: Unique identifier for the data
            
        Returns:
            True if data exists, False otherwise
        """
        pass
    
    @abstractmethod
    def list_keys(self) -> List[str]:
        """
        List all available keys in storage.
        
        Returns:
            List of keys
        """
        pass


# ============================================================================
# CONCRETE IMPLEMENTATION 1: File System Storage
# ============================================================================
# This implementation hides all the complexity of:
# - File path management
# - Directory creation
# - File I/O operations
# - Error handling for disk operations

class FileSystemStorage(Storage):
    """
    File system storage implementation.
    
    This hides all the complexity of:
    - File path sanitization and generation
    - Directory structure management
    - File read/write operations
    - Disk space management
    - Permission handling
    """
    
    def __init__(self, base_path: str = "./storage"):
        """
        Initialize file system storage.
        
        Args:
            base_path: Root directory for storing files
        """
        self.base_path = Path(base_path)
        self.metadata_path = self.base_path / ".metadata"
        self._initialize_storage()
    
    def _initialize_storage(self):
        """Initialize storage directory structure"""
        # Create main storage directory
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # Create metadata directory
        self.metadata_path.mkdir(parents=True, exist_ok=True)
        
        print(f"  [FileSystem] Initialized storage at: {self.base_path}")
    
    def _get_file_path(self, key: str) -> Path:
        """Convert key to safe filename and return full path"""
        # Sanitize key to be filesystem-safe
        safe_key = self._sanitize_key(key)
        return self.base_path / safe_key
    
    def _get_metadata_path(self, key: str) -> Path:
        """Get path for metadata file"""
        safe_key = self._sanitize_key(key)
        return self.metadata_path / f"{safe_key}.meta"
    
    def _sanitize_key(self, key: str) -> str:
        """Make key filesystem-safe"""
        # Replace problematic characters
        unsafe_chars = '/\\:*?"<>|'
        safe_key = key
        for char in unsafe_chars:
            safe_key = safe_key.replace(char, '_')
        return safe_key
    
    def save(self, key: str, data: bytes) -> StorageResult:
        """Save data to file system"""
        try:
            file_path = self._get_file_path(key)
            
            # Write data to file
            file_path.write_bytes(data)
            
            # Save metadata
            metadata = {
                'key': key,
                'saved_at': datetime.now().isoformat(),
                'size': len(data),
                'path': str(file_path)
            }
            
            meta_path = self._get_metadata_path(key)
            meta_path.write_text(json.dumps(metadata, indent=2))
            
            print(f"  [FileSystem] Saved file: {file_path.name} ({len(data)} bytes)")
            
            return StorageResult(
                success=True,
                key=key,
                message=f"Data saved successfully to {file_path}"
            )
        except (OSError, IOError) as e:
            print(f"  [FileSystem] Error saving {key}: {e}")
            return StorageResult(
                success=False,
                key=key,
                message=f"Failed to save data: {str(e)}"
            )
    
    def load(self, key: str) -> StorageResult:
        """Load data from file system"""
        try:
            file_path = self._get_file_path(key)
            
            if not file_path.exists():
                return StorageResult(
                    success=False,
                    key=key,
                    message=f"File not found: {key}"
                )
            
            data = file_path.read_bytes()
            
            print(f"  [FileSystem] Loaded file: {file_path.name} ({len(data)} bytes)")
            
            return StorageResult(
                success=True,
                key=key,
                message="Data loaded successfully",
                document=Document(
                    id=key,
                    name=file_path.name,
                    content=data,
                    created_at=datetime.fromtimestamp(file_path.stat().st_ctime),
                    updated_at=datetime.fromtimestamp(file_path.stat().st_mtime),
                    size=len(data),
                    mime_type="application/octet-stream"
                )
            )
        except (OSError, IOError) as e:
            return StorageResult(
                success=False,
                key=key,
                message=f"Failed to load data: {str(e)}"
            )
    
    def delete(self, key: str) -> StorageResult:
        """Delete data from file system"""
        try:
            file_path = self._get_file_path(key)
            meta_path = self._get_metadata_path(key)
            
            deleted = False
            
            if file_path.exists():
                file_path.unlink()
                deleted = True
            
            if meta_path.exists():
                meta_path.unlink()
            
            if deleted:
                print(f"  [FileSystem] Deleted file: {file_path.name}")
                return StorageResult(
                    success=True,
                    key=key,
                    message=f"Data deleted successfully"
                )
            else:
                return StorageResult(
                    success=False,
                    key=key,
                    message=f"File not found: {key}"
                )
        except (OSError, IOError) as e:
            return StorageResult(
                success=False,
                key=key,
                message=f"Failed to delete data: {str(e)}"
            )
    
    def exists(self, key: str) -> bool:
        """Check if file exists"""
        return self._get_file_path(key).exists()
    
    def list_keys(self) -> List[str]:
        """List all stored keys"""
        keys = []
        for file_path in self.base_path.iterdir():
            if file_path.is_file() and not file_path.name.startswith('.'):
                # Try to find corresponding metadata
                meta_path = self.metadata_path / f"{file_path.name}.meta"
                if meta_path.exists():
                    try:
                        metadata = json.loads(meta_path.read_text())
                        keys.append(metadata.get('key', file_path.name))
                    except:
                        keys.append(file_path.name)
                else:
                    keys.append(file_path.name)
        return keys
    
    def clear(self):
        """Clear all stored data (helper method for testing)"""
        if self.base_path.exists():
            shutil.rmtree(self.base_path)
        self._initialize_storage()


# ============================================================================
# CONCRETE IMPLEMENTATION 2: In-Memory Storage
# ============================================================================
# This implementation hides all the complexity of:
# - Memory data structures
# - Concurrent access management
# - Serialization/deserialization
# - Metadata tracking

class InMemoryStorage(Storage):
    """
    In-memory storage implementation.
    
    Completely different implementation, but same interface!
    The client code doesn't care about the differences.
    
    Useful for:
    - Unit testing
    - Development environments
    - Caching layers
    """
    
    def __init__(self):
        """Initialize in-memory storage"""
        self._data: Dict[str, bytes] = {}
        self._metadata: Dict[str, Dict] = {}
        print(f"  [InMemory] Initialized storage in memory")
    
    def save(self, key: str, data: bytes) -> StorageResult:
        """Save data to memory"""
        try:
            # Store data
            self._data[key] = data
            
            # Store metadata
            self._metadata[key] = {
                'key': key,
                'saved_at': datetime.now().isoformat(),
                'size': len(data),
                'in_memory': True
            }
            
            print(f"  [InMemory] Saved key: {key} ({len(data)} bytes)")
            
            return StorageResult(
                success=True,
                key=key,
                message="Data saved successfully in memory"
            )
        except Exception as e:
            return StorageResult(
                success=False,
                key=key,
                message=f"Failed to save data: {str(e)}"
            )
    
    def load(self, key: str) -> StorageResult:
        """Load data from memory"""
        try:
            if key not in self._data:
                return StorageResult(
                    success=False,
                    key=key,
                    message=f"Key not found: {key}"
                )
            
            data = self._data[key]
            metadata = self._metadata.get(key, {})
            
            print(f"  [InMemory] Loaded key: {key} ({len(data)} bytes)")
            
            return StorageResult(
                success=True,
                key=key,
                message="Data loaded successfully from memory",
                document=Document(
                    id=key,
                    name=key,
                    content=data,
                    created_at=datetime.fromisoformat(metadata.get('saved_at', datetime.now().isoformat())),
                    updated_at=datetime.fromisoformat(metadata.get('saved_at', datetime.now().isoformat())),
                    size=len(data),
                    mime_type="application/octet-stream"
                )
            )
        except Exception as e:
            return StorageResult(
                success=False,
                key=key,
                message=f"Failed to load data: {str(e)}"
            )
    
    def delete(self, key: str) -> StorageResult:
        """Delete data from memory"""
        try:
            if key in self._data:
                del self._data[key]
                
            if key in self._metadata:
                del self._metadata[key]
                
            print(f"  [InMemory] Deleted key: {key}")
            
            return StorageResult(
                success=True,
                key=key,
                message="Data deleted successfully from memory"
            )
        except Exception as e:
            return StorageResult(
                success=False,
                key=key,
                message=f"Failed to delete data: {str(e)}"
            )
    
    def exists(self, key: str) -> bool:
        """Check if key exists in memory"""
        return key in self._data
    
    def list_keys(self) -> List[str]:
        """List all stored keys"""
        return list(self._data.keys())
    
    def clear(self):
        """Clear all stored data"""
        self._data.clear()
        self._metadata.clear()
        print("  [InMemory] Cleared all data")


# ============================================================================
# CONCRETE IMPLEMENTATION 3: Encrypted Storage (Bonus)
# ============================================================================
# Another implementation demonstrating how easy it is to extend the system

class EncryptedFileSystemStorage(FileSystemStorage):
    """
    Encrypted file system storage.
    
    Adds encryption layer without changing the interface.
    Demonstrates how abstraction allows adding features transparently.
    """
    
    def __init__(self, base_path: str = "./encrypted_storage", encryption_key: str = "default-key"):
        super().__init__(base_path)
        self.encryption_key = encryption_key
        print(f"  [EncryptedFS] Initialized with encryption enabled")
    
    def _encrypt(self, data: bytes) -> bytes:
        """Simulate encryption (simple XOR for demonstration)"""
        # In production, use proper encryption like AES
        key = self.encryption_key.encode()
        encrypted = bytearray()
        for i, byte in enumerate(data):
            encrypted.append(byte ^ key[i % len(key)])
        return bytes(encrypted)
    
    def _decrypt(self, data: bytes) -> bytes:
        """Simulate decryption"""
        # XOR with same key decrypts
        return self._encrypt(data)
    
    def save(self, key: str, data: bytes) -> StorageResult:
        """Save encrypted data"""
        encrypted_data = self._encrypt(data)
        print(f"  [EncryptedFS] Encrypting {len(data)} bytes → {len(encrypted_data)} bytes")
        return super().save(f"enc_{key}", encrypted_data)
    
    def load(self, key: str) -> StorageResult:
        """Load and decrypt data"""
        result = super().load(f"enc_{key}")
        if result.success and result.document:
            decrypted_data = self._decrypt(result.document.content)
            result.document.content = decrypted_data
            print(f"  [EncryptedFS] Decrypted {len(decrypted_data)} bytes")
        return result


# ============================================================================
# CLIENT CODE: Uses Abstraction
# ============================================================================
# This code doesn't know or care which storage backend is being used.
# It works with ANY storage that implements the interface.

class DocumentManager:
    """
    Document manager that uses storage backends.
    
    This demonstrates the power of abstraction:
    - The manager doesn't know about filesystem/memory internals
    - We can swap storage backends without changing this code
    - The complexity is hidden behind the interface
    """
    
    def __init__(self, storage: Storage):
        """
        Dependency Injection: We inject the storage backend.
        This makes the system flexible and testable.
        """
        self.storage = storage
        self._documents: Dict[str, Document] = {}
        print(f"  [DocumentManager] Initialized with {storage.__class__.__name__}")
    
    def create_document(self, doc_id: str, content: str, name: Optional[str] = None) -> StorageResult:
        """
        Create a new document.
        
        Notice: This method doesn't care if it's filesystem, memory, or any
        other storage backend. It just uses the interface!
        """
        print(f"\n📄 Creating document: {doc_id}")
        
        # Convert string to bytes
        data = content.encode('utf-8')
        
        # Save using the storage backend
        result = self.storage.save(doc_id, data)
        
        if result.success:
            # Create document object
            now = datetime.now()
            document = Document(
                id=doc_id,
                name=name or doc_id,
                content=data,
                created_at=now,
                updated_at=now,
                size=len(data),
                mime_type="text/plain"
            )
            self._documents[doc_id] = document
            print(f"  ✅ Document created: {doc_id} ({len(data)} bytes)")
        
        return result
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """
        Retrieve a document.
        
        Same interface, regardless of storage backend!
        """
        print(f"\n📖 Retrieving document: {doc_id}")
        
        result = self.storage.load(doc_id)
        
        if result.success and result.document:
            print(f"  ✅ Document retrieved: {doc_id} ({result.document.size} bytes)")
            return result.document
        else:
            print(f"  ❌ Document not found: {doc_id}")
            return None
    
    def update_document(self, doc_id: str, content: str) -> bool:
        """Update an existing document"""
        print(f"\n✏️ Updating document: {doc_id}")
        
        if not self.storage.exists(doc_id):
            print(f"  ❌ Document not found: {doc_id}")
            return False
        
        data = content.encode('utf-8')
        result = self.storage.save(doc_id, data)
        
        if result.success:
            print(f"  ✅ Document updated: {doc_id} ({len(data)} bytes)")
            return True
        return False
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document"""
        print(f"\n🗑️ Deleting document: {doc_id}")
        
        result = self.storage.delete(doc_id)
        
        if result.success:
            print(f"  ✅ Document deleted: {doc_id}")
            return True
        else:
            print(f"  ❌ Document not found: {doc_id}")
            return False
    
    def list_documents(self) -> List[str]:
        """List all document IDs"""
        print(f"\n📋 Listing documents...")
        keys = self.storage.list_keys()
        print(f"  Found {len(keys)} document(s): {', '.join(keys) if keys else 'none'}")
        return keys


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_storage_abstraction():
    """
    Demonstrate how abstraction allows us to swap storage implementations
    without changing client code.
    """
    print("=" * 80)
    print("EXERCISE 1.1: Storage Abstraction")
    print("=" * 80)
    
    print("\n📚 KEY CONCEPTS:")
    print("   • Abstraction hides storage implementation complexity")
    print("   • Interfaces define contracts between components")
    print("   • Clients depend on interfaces, not implementations")
    print("   • Different backends can be swapped transparently")
    print("   • New backends can be added without modifying client code")
    
    print("\n" + "=" * 80)
    print("SCENARIO 1: File System Storage Backend")
    print("=" * 80)
    
    # Create file system storage (hides all filesystem complexity)
    file_storage = FileSystemStorage("./test_storage")
    doc_manager_fs = DocumentManager(file_storage)
    
    # Create documents - notice we don't see the filesystem complexity!
    doc_manager_fs.create_document("report-2024", "Annual Report 2024: Revenue increased by 25%", "annual_report.txt")
    doc_manager_fs.create_document("invoice-123", "Invoice #123 - $1,500.00 due 30 days", "invoice_123.pdf")
    
    # Retrieve documents
    doc_manager_fs.get_document("report-2024")
    doc_manager_fs.get_document("nonexistent")  # Handle missing documents
    
    # List all documents
    doc_manager_fs.list_documents()
    
    # Update document
    doc_manager_fs.update_document("report-2024", "Annual Report 2024: Revenue increased by 35%")
    
    # Delete document
    doc_manager_fs.delete_document("invoice-123")
    
    print("\n" + "=" * 80)
    print("SCENARIO 2: In-Memory Storage Backend (No Code Changes!)")
    print("=" * 80)
    
    # Switch to in-memory storage - just change the implementation!
    # The DocumentManager code doesn't need to change at all!
    memory_storage = InMemoryStorage()
    doc_manager_memory = DocumentManager(memory_storage)
    
    # Same interface, completely different implementation!
    doc_manager_memory.create_document("config", '{"theme": "dark", "language": "en"}', "config.json")
    doc_manager_memory.create_document("user-preferences", "font_size=12;notifications=true", "preferences.ini")
    
    doc_manager_memory.get_document("config")
    doc_manager_memory.list_documents()
    doc_manager_memory.delete_document("user-preferences")
    
    print("\n" + "=" * 80)
    print("SCENARIO 3: Encrypted File System Storage (Bonus)")
    print("=" * 80)
    
    # Another implementation, same interface!
    encrypted_storage = EncryptedFileSystemStorage("./encrypted_test", "super-secret-key-123")
    doc_manager_encrypted = DocumentManager(encrypted_storage)
    
    doc_manager_encrypted.create_document("secret-data", "This is confidential information!", "secret.txt")
    doc_manager_encrypted.get_document("secret-data")
    
    print("\n" + "=" * 80)
    print("SCENARIO 4: Runtime Storage Backend Swapping")
    print("=" * 80)
    
    # Create a document manager and swap storage at runtime
    print("\n🔄 Creating document manager with file storage...")
    doc_manager = DocumentManager(file_storage)
    doc_manager.create_document("important-doc", "This document is in the filesystem")
    
    print("\n🔄 Switching to memory storage at runtime...")
    doc_manager.storage = memory_storage
    doc_manager.create_document("important-doc", "This document is in memory (same key, different storage!)")
    doc_manager.get_document("important-doc")
    
    print("\n" + "=" * 80)
    print("KEY INSIGHT: Architecture Enables Flexibility")
    print("=" * 80)
    print("""
    By using abstraction and interfaces:
    
    1. ✅ We can swap storage backends without changing business logic
    2. ✅ We can test with fast in-memory implementations
    3. ✅ We can support multiple storage backends simultaneously
    4. ✅ New developers don't need to understand storage internals
    5. ✅ Changes to storage systems don't break our document code
    6. ✅ We can add features (encryption, compression) transparently
    
    This is the power of good software architecture!
    """)
    
    print("\n" + "=" * 80)
    print("REAL-WORLD BUSINESS BENEFITS")
    print("=" * 80)
    print("""
    In a real document management system:
    
    • Cost optimization: Move between S3, Azure Blob, or local storage based on cost
    • Performance: Cache frequently accessed documents in memory
    • Compliance: Add encryption for sensitive documents without changing workflows
    • Migration: Switch storage providers without downtime
    • Testing: Run integration tests without actual storage costs
    
    All made possible by architectural abstraction!
    """)
    
    # Clean up
    print("\n" + "=" * 80)
    print("CLEANING UP")
    print("=" * 80)
    file_storage.clear()
    encrypted_storage.clear()
    memory_storage.clear()
    print("\n✅ All test data cleaned up successfully!")


if __name__ == "__main__":
    demonstrate_storage_abstraction()
