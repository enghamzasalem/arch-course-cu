from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from datetime import datetime


# ============================================================================
# DATA MODELS (Logical Entities)
# ============================================================================
# These classes represent the core data structures of the system.

@dataclass
class Book:
    title: str
    authour: str
    publisher: str
    year: int
    loan_status: bool = False

@dataclass
class Member:
    name: str
    email: str
    address: str
    loaned_books: List[Book]
    LOAN_LIMIT = 5


# ============================================================================
# Specialized Managers
# ============================================================================
# Each manager is a modular component responsible for one functional area.

class BookManager:
    def __init__(self):
        self.books = []

    def add_book(self, book: Book):
        self.books.append(book)
        print(f"Book '{book.title}' added successfully.")

    def list_books(self) -> List[dict]:
        return self.books

class MemberManager:
    def __init__(self):
        self.members = []

    def register_member(self, member: Member):
        self.members.append(member)
        print(f"Member '{member.name}' registered successfully.")


class LoanManager:
    def __init__(self):
        self.loans = []

    def loan_book(self, book: Book, member: Member):
        if len(member.loaned_books) >= Member.LOAN_LIMIT:
            print(f"Member '{member.name}' has reached the loan limit.")
            return False
        if book.loan_status:
            print(f"Book '{book.title}' is already loaned out.")
            return False
        book.loan_status = True
        member.loaned_books.append(book)
        self.loans.append((book, member))
        print(f"Book '{book.title}' loaned to member '{member.name}' successfully.")
        return True


# ----------------------------------------------------------------------------
# UTILITY COMPONENT
# ----------------------------------------------------------------------------
# A standalone service for specialized calculations.

class FineCalculator:
    def calculate(self, due_date: datetime) -> float:
        overdue_days = (datetime.now() - due_date).days
        return max(0, overdue_days * 0.50)




# ============================================================================
# The Orchestrator (Mediator)
# ============================================================================
# LibrarySystem acts as the central hub, coordinating between managers.

class LibrarySystem:
    def __init__(self):
        self.book_manager = BookManager()
        self.member_manager = MemberManager()
        self.loan_manager = LoanManager()
        self.fine_calculator = FineCalculator()

    def borrow_book(self, book: Book, member: Member):
        return self.loan_manager.loan_book(book, member)

if __name__ == "__main__":
    lib = LibrarySystem()
    book = Book(title="The Great Gatsby", authour="F. Scott Fitzgerald", publisher="Scribner", year=1925)
    lib.book_manager.add_book(book)
    member = Member(name="Alice", email="alice@ilovebooks.com", address="123 Book St", loaned_books=[])
    lib.member_manager.register_member(member)
    lib.borrow_book(book, member)
     


               

