#!/usr/bin/env python3
"""
Exercise 2.1: Break Down a Monolithic System 🟢

This example demonstrates:
- Identifying distinct responsibilities in a monolithic system
- Separating concerns into independent, testable components
- Orchestrating components through dependency injection
- Creating modular, maintainable architecture

Business Scenario: Library Management System
- Original: 200+ line monolithic class doing everything
- Refactored: 6 focused components with single responsibilities
- Benefits: Testability, maintainability, parallel development
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from enum import Enum
import uuid
import json


# ============================================================================
# PART 1: THE PROBLEM - MONOLITHIC SYSTEM (BEFORE)
# ============================================================================
"""
class LibrarySystem:
    def __init__(self):
        self.books = {}           # Book catalog
        self.members = {}         # Member registry
        self.loans = {}           # Active loans
        self.fines = {}           # Outstanding fines
        self.notifications = []   # Notification history
        self.fine_rate = 0.50     # Fine per day
    
    def add_book(self, isbn, title, author, year, copies):
        # Book management
        pass
    
    def remove_book(self, isbn):
        # Book management
        pass
    
    def find_books(self, query):
        # Book search
        pass
    
    def register_member(self, name, email, phone):
        # Member management
        pass
    
    def update_member(self, member_id, **kwargs):
        # Member management
        pass
    
    def deactivate_member(self, member_id):
        # Member management
        pass
    
    def borrow_book(self, member_id, isbn):
        # Loan management + availability check + member validation + due dates
        pass
    
    def return_book(self, loan_id):
        # Loan management + fine calculation + book availability
        pass
    
    def renew_loan(self, loan_id):
        # Loan management + eligibility check
        pass
    
    def calculate_fine(self, loan_id):
        # Fine calculation logic
        pass
    
    def pay_fine(self, member_id, amount):
        # Fine payment processing
        pass
    
    def send_overdue_notice(self, member_id):
        # Notification + fine calculation + member contact
        pass
    
    def send_reminder(self, member_id):
        # Notification + loan tracking
        pass
    
    def generate_report(self, report_type):
        # Reporting + aggregating data from all components
        pass
    
    # ... 10+ more methods mixing ALL concerns
    # TOTAL: 25+ methods, 1 monster class
"""


# ============================================================================
# PART 2: THE SOLUTION - IDENTIFYING DISTINCT COMPONENTS
# ============================================================================
# Identified Components:
# 1. BookManager - Book catalog and inventory
# 2. MemberManager - Member registry and profiles
# 3. LoanManager - Borrowing, returning, renewals
# 4. FineCalculator - Fine calculation and payments
# 5. NotificationService - Member communications
# 6. ReportingEngine - Data aggregation and reports
# 7. LibraryOrchestrator - Composes all components


# ============================================================================
# CORE DOMAIN MODELS
# ============================================================================

@dataclass
class Book:
    """Book entity"""
    isbn: str
    title: str
    author: str
    year: int
    total_copies: int = 1
    available_copies: int = 1
    location: str = "Main Shelf"
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def is_available(self) -> bool:
        return self.available_copies > 0
    
    def borrow_copy(self) -> bool:
        if self.available_copies > 0:
            self.available_copies -= 1
            return True
        return False
    
    def return_copy(self) -> bool:
        if self.available_copies < self.total_copies:
            self.available_copies += 1
            return True
        return False


@dataclass
class Member:
    """Library member entity"""
    member_id: str
    name: str
    email: str
    phone: str
    join_date: datetime = field(default_factory=datetime.now)
    active: bool = True
    membership_level: str = "standard"  # standard, premium, student
    max_loans: int = 5
    current_loans: int = 0
    
    def can_borrow(self) -> bool:
        return self.active and self.current_loans < self.max_loans
    
    def increment_loans(self):
        self.current_loans += 1
    
    def decrement_loans(self):
        self.current_loans = max(0, self.current_loans - 1)


@dataclass
class Loan:
    """Book loan transaction"""
    loan_id: str
    member_id: str
    isbn: str
    book_title: str
    borrowed_date: datetime = field(default_factory=datetime.now)
    due_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=14))
    returned_date: Optional[datetime] = None
    renewed_count: int = 0
    status: str = "active"  # active, returned, overdue
    
    @property
    def is_overdue(self) -> bool:
        if self.returned_date:
            return False
        return datetime.now() > self.due_date
    
    @property
    def days_overdue(self) -> int:
        if not self.is_overdue:
            return 0
        return (datetime.now() - self.due_date).days


@dataclass
class Fine:
    """Library fine"""
    fine_id: str
    member_id: str
    loan_id: str
    amount: float
    reason: str
    issued_date: datetime = field(default_factory=datetime.now)
    paid_date: Optional[datetime] = None
    status: str = "pending"  # pending, paid, waived
    
    def pay(self):
        self.paid_date = datetime.now()
        self.status = "paid"


@dataclass
class Notification:
    """Notification record"""
    notification_id: str
    member_id: str
    type: str  # overdue, reminder, welcome, receipt
    subject: str
    message: str
    sent_date: datetime = field(default_factory=datetime.now)
    status: str = "sent"  # sent, failed, delivered


# ============================================================================
# COMPONENT 1: BOOK MANAGER
# ============================================================================

class BookManager:
    """
    Responsible for ALL book-related operations:
    - Catalog management (add, update, remove)
    - Inventory tracking
    - Book search and discovery
    - Availability management
    """
    
    def __init__(self):
        self._books: Dict[str, Book] = {}  # ISBN -> Book
        self._isbn_index: Dict[str, str] = {}  # ISBN lookup
        self._title_index: Dict[str, Set[str]] = {}  # title -> ISBNs
        self._author_index: Dict[str, Set[str]] = {}  # author -> ISBNs
        print("  [BookManager] Initialized")
    
    def add_book(self, isbn: str, title: str, author: str, 
                 year: int, copies: int = 1) -> Book:
        """Add a new book to catalog"""
        if isbn in self._books:
            # Update existing book
            book = self._books[isbn]
            book.total_copies += copies
            book.available_copies += copies
            print(f"  [BookManager] Updated book '{title}', added {copies} copy(ies)")
        else:
            # Create new book
            book = Book(
                isbn=isbn,
                title=title,
                author=author,
                year=year,
                total_copies=copies,
                available_copies=copies
            )
            self._books[isbn] = book
            self._isbn_index[isbn] = isbn
            
            # Index by title
            title_lower = title.lower()
            if title_lower not in self._title_index:
                self._title_index[title_lower] = set()
            self._title_index[title_lower].add(isbn)
            
            # Index by author
            author_lower = author.lower()
            if author_lower not in self._author_index:
                self._author_index[author_lower] = set()
            self._author_index[author_lower].add(isbn)
            
            print(f"  [BookManager] Added new book '{title}' by {author}")
        
        return self._books[isbn]
    
    def remove_book(self, isbn: str) -> bool:
        """Remove a book from catalog"""
        if isbn in self._books:
            book = self._books[isbn]
            del self._books[isbn]
            print(f"  [BookManager] Removed book '{book.title}'")
            return True
        return False
    
    def get_book(self, isbn: str) -> Optional[Book]:
        """Get book by ISBN"""
        return self._books.get(isbn)
    
    def find_books_by_title(self, title: str) -> List[Book]:
        """Find books by title (partial match)"""
        title_lower = title.lower()
        results = []
        
        for indexed_title, isbns in self._title_index.items():
            if title_lower in indexed_title:
                for isbn in isbns:
                    if isbn in self._books:
                        results.append(self._books[isbn])
        
        return results
    
    def find_books_by_author(self, author: str) -> List[Book]:
        """Find books by author (partial match)"""
        author_lower = author.lower()
        results = []
        
        for indexed_author, isbns in self._author_index.items():
            if author_lower in indexed_author:
                for isbn in isbns:
                    if isbn in self._books:
                        results.append(self._books[isbn])
        
        return results
    
    def get_all_books(self) -> List[Book]:
        """Get all books in catalog"""
        return list(self._books.values())
    
    def is_available(self, isbn: str) -> bool:
        """Check if book is available"""
        book = self.get_book(isbn)
        return book is not None and book.is_available()
    
    def borrow_book(self, isbn: str) -> bool:
        """Process book borrowing (update availability)"""
        book = self.get_book(isbn)
        if book:
            return book.borrow_copy()
        return False
    
    def return_book(self, isbn: str) -> bool:
        """Process book return (update availability)"""
        book = self.get_book(isbn)
        if book:
            return book.return_copy()
        return False
    
    def get_inventory_stats(self) -> Dict:
        """Get inventory statistics"""
        total_books = len(self._books)
        total_copies = sum(b.total_copies for b in self._books.values())
        available_copies = sum(b.available_copies for b in self._books.values())
        
        return {
            'unique_titles': total_books,
            'total_copies': total_copies,
            'available_copies': available_copies,
            'checked_out_copies': total_copies - available_copies
        }


# ============================================================================
# COMPONENT 2: MEMBER MANAGER
# ============================================================================

class MemberManager:
    """
    Responsible for ALL member-related operations:
    - Registration and profiles
    - Member status and eligibility
    - Contact information
    - Membership levels
    """
    
    def __init__(self):
        self._members: Dict[str, Member] = {}  # member_id -> Member
        self._email_index: Dict[str, str] = {}  # email -> member_id
        print("  [MemberManager] Initialized")
    
    def register_member(self, name: str, email: str, phone: str, 
                       membership_level: str = "standard") -> Member:
        """Register a new member"""
        if email in self._email_index:
            raise ValueError(f"Member with email {email} already exists")
        
        member_id = f"M{str(uuid.uuid4())[:8].upper()}"
        
        # Configure max loans based on membership
        max_loans = {
            "standard": 5,
            "premium": 10,
            "student": 3
        }.get(membership_level, 5)
        
        member = Member(
            member_id=member_id,
            name=name,
            email=email,
            phone=phone,
            membership_level=membership_level,
            max_loans=max_loans
        )
        
        self._members[member_id] = member
        self._email_index[email] = member_id
        
        print(f"  [MemberManager] Registered member: {name} ({member_id})")
        return member
    
    def get_member(self, member_id: str) -> Optional[Member]:
        """Get member by ID"""
        return self._members.get(member_id)
    
    def get_member_by_email(self, email: str) -> Optional[Member]:
        """Get member by email"""
        member_id = self._email_index.get(email)
        if member_id:
            return self.get_member(member_id)
        return None
    
    def update_member(self, member_id: str, **kwargs) -> Optional[Member]:
        """Update member information"""
        member = self.get_member(member_id)
        if not member:
            return None
        
        # Update allowed fields
        allowed_fields = {'name', 'email', 'phone', 'membership_level'}
        for key, value in kwargs.items():
            if key in allowed_fields:
                # Update email index if email changes
                if key == 'email' and member.email != value:
                    del self._email_index[member.email]
                    self._email_index[value] = member_id
                
                setattr(member, key, value)
        
        print(f"  [MemberManager] Updated member: {member.name}")
        return member
    
    def deactivate_member(self, member_id: str) -> bool:
        """Deactivate a member"""
        member = self.get_member(member_id)
        if member:
            member.active = False
            print(f"  [MemberManager] Deactivated member: {member.name}")
            return True
        return False
    
    def activate_member(self, member_id: str) -> bool:
        """Reactivate a member"""
        member = self.get_member(member_id)
        if member:
            member.active = True
            print(f"  [MemberManager] Activated member: {member.name}")
            return True
        return False
    
    def increment_loans(self, member_id: str) -> bool:
        """Increment member's active loan count"""
        member = self.get_member(member_id)
        if member:
            member.increment_loans()
            return True
        return False
    
    def decrement_loans(self, member_id: str) -> bool:
        """Decrement member's active loan count"""
        member = self.get_member(member_id)
        if member:
            member.decrement_loans()
            return True
        return False
    
    def can_borrow(self, member_id: str) -> bool:
        """Check if member can borrow more books"""
        member = self.get_member(member_id)
        return member is not None and member.can_borrow()
    
    def get_all_members(self) -> List[Member]:
        """Get all registered members"""
        return list(self._members.values())
    
    def get_active_members(self) -> List[Member]:
        """Get active members only"""
        return [m for m in self._members.values() if m.active]
    
    def get_member_stats(self) -> Dict:
        """Get member statistics"""
        total = len(self._members)
        active = len([m for m in self._members.values() if m.active])
        total_loans = sum(m.current_loans for m in self._members.values())
        
        return {
            'total_members': total,
            'active_members': active,
            'inactive_members': total - active,
            'total_active_loans': total_loans
        }


# ============================================================================
# COMPONENT 3: LOAN MANAGER
# ============================================================================

class LoanManager:
    """
    Responsible for ALL loan-related operations:
    - Borrowing process
    - Returns and renewals
    - Due date tracking
    - Overdue detection
    """
    
    def __init__(self, book_manager: BookManager, member_manager: MemberManager):
        self.book_manager = book_manager
        self.member_manager = member_manager
        self._loans: Dict[str, Loan] = {}  # loan_id -> Loan
        self._member_loans: Dict[str, Set[str]] = {}  # member_id -> Set[loan_id]
        self._book_loans: Dict[str, Set[str]] = {}  # isbn -> Set[loan_id]
        print("  [LoanManager] Initialized")
    
    def borrow_book(self, member_id: str, isbn: str) -> Optional[Loan]:
        """Process book borrowing"""
        # Validate member
        member = self.member_manager.get_member(member_id)
        if not member:
            print(f"  [LoanManager] ❌ Member not found: {member_id}")
            return None
        
        if not member.can_borrow():
            print(f"  [LoanManager] ❌ Member {member_id} cannot borrow (limit reached)")
            return None
        
        # Validate book availability
        if not self.book_manager.is_available(isbn):
            print(f"  [LoanManager] ❌ Book {isbn} not available")
            return None
        
        book = self.book_manager.get_book(isbn)
        
        # Process borrowing
        self.book_manager.borrow_book(isbn)
        self.member_manager.increment_loans(member_id)
        
        # Create loan record
        loan_id = f"L{str(uuid.uuid4())[:8].upper()}"
        loan = Loan(
            loan_id=loan_id,
            member_id=member_id,
            isbn=isbn,
            book_title=book.title
        )
        
        self._loans[loan_id] = loan
        
        # Index loans
        if member_id not in self._member_loans:
            self._member_loans[member_id] = set()
        self._member_loans[member_id].add(loan_id)
        
        if isbn not in self._book_loans:
            self._book_loans[isbn] = set()
        self._book_loans[isbn].add(loan_id)
        
        print(f"  [LoanManager] ✅ Book '{book.title}' borrowed by {member.name}")
        print(f"  [LoanManager]    Due: {loan.due_date.strftime('%Y-%m-%d')}")
        
        return loan
    
    def return_book(self, loan_id: str) -> Optional[Loan]:
        """Process book return"""
        loan = self._loans.get(loan_id)
        if not loan:
            print(f"  [LoanManager] ❌ Loan not found: {loan_id}")
            return None
        
        if loan.returned_date:
            print(f"  [LoanManager] ❌ Book already returned")
            return None
        
        # Update loan
        loan.returned_date = datetime.now()
        loan.status = "returned"
        
        # Update book and member
        self.book_manager.return_book(loan.isbn)
        self.member_manager.decrement_loans(loan.member_id)
        
        book = self.book_manager.get_book(loan.isbn)
        member = self.member_manager.get_member(loan.member_id)
        
        print(f"  [LoanManager] ✅ Book '{book.title}' returned by {member.name}")
        
        return loan
    
    def renew_loan(self, loan_id: str, days: int = 7) -> Optional[Loan]:
        """Renew a loan"""
        loan = self._loans.get(loan_id)
        if not loan:
            print(f"  [LoanManager] ❌ Loan not found: {loan_id}")
            return None
        
        if loan.returned_date:
            print(f"  [LoanManager] ❌ Cannot renew - already returned")
            return None
        
        if loan.renewed_count >= 2:
            print(f"  [LoanManager] ❌ Maximum renewals reached")
            return None
        
        # Extend due date
        loan.due_date += timedelta(days=days)
        loan.renewed_count += 1
        
        print(f"  [LoanManager] ✅ Loan renewed, new due date: {loan.due_date.strftime('%Y-%m-%d')}")
        
        return loan
    
    def get_member_loans(self, member_id: str, active_only: bool = True) -> List[Loan]:
        """Get loans for a member"""
        loan_ids = self._member_loans.get(member_id, set())
        loans = []
        
        for loan_id in loan_ids:
            loan = self._loans.get(loan_id)
            if loan:
                if active_only and loan.returned_date:
                    continue
                loans.append(loan)
        
        return loans
    
    def get_book_loans(self, isbn: str, active_only: bool = True) -> List[Loan]:
        """Get loans for a book"""
        loan_ids = self._book_loans.get(isbn, set())
        loans = []
        
        for loan_id in loan_ids:
            loan = self._loans.get(loan_id)
            if loan:
                if active_only and loan.returned_date:
                    continue
                loans.append(loan)
        
        return loans
    
    def get_overdue_loans(self) -> List[Loan]:
        """Get all overdue loans"""
        overdue = []
        for loan in self._loans.values():
            if not loan.returned_date and loan.is_overdue:
                overdue.append(loan)
        
        return overdue
    
    def get_active_loans(self) -> List[Loan]:
        """Get all active loans"""
        return [l for l in self._loans.values() if not l.returned_date]
    
    def get_loan_stats(self) -> Dict:
        """Get loan statistics"""
        total = len(self._loans)
        active = len([l for l in self._loans.values() if not l.returned_date])
        overdue = len(self.get_overdue_loans())
        
        return {
            'total_loans': total,
            'active_loans': active,
            'returned_loans': total - active,
            'overdue_loans': overdue
        }


# ============================================================================
# COMPONENT 4: FINE CALCULATOR
# ============================================================================

class FineCalculator:
    """
    Responsible for ALL fine-related operations:
    - Fine calculation logic
    - Fine assessment
    - Payment processing
    - Fine waivers
    """
    
    def __init__(self, loan_manager: LoanManager, member_manager: MemberManager):
        self.loan_manager = loan_manager
        self.member_manager = member_manager
        self._fines: Dict[str, Fine] = {}  # fine_id -> Fine
        self._member_fines: Dict[str, Set[str]] = {}  # member_id -> Set[fine_id]
        self._daily_fine_rate = 0.50  # $0.50 per day
        print("  [FineCalculator] Initialized")
    
    def calculate_fine(self, loan_id: str) -> Optional[float]:
        """Calculate fine for an overdue loan"""
        loan = self.loan_manager._loans.get(loan_id)
        if not loan:
            return None
        
        if not loan.is_overdue:
            return 0.0
        
        days = loan.days_overdue
        fine_amount = days * self._daily_fine_rate
        
        return round(fine_amount, 2)
    
    def assess_fine(self, loan_id: str) -> Optional[Fine]:
        """Assess a fine for an overdue loan"""
        loan = self.loan_manager._loans.get(loan_id)
        if not loan:
            return None
        
        # Check if fine already exists for this loan
        for fine in self._fines.values():
            if fine.loan_id == loan_id and fine.status == "pending":
                print(f"  [FineCalculator] Fine already exists for loan {loan_id}")
                return fine
        
        fine_amount = self.calculate_fine(loan_id)
        if fine_amount <= 0:
            return None
        
        # Create fine
        fine_id = f"F{str(uuid.uuid4())[:8].upper()}"
        fine = Fine(
            fine_id=fine_id,
            member_id=loan.member_id,
            loan_id=loan_id,
            amount=fine_amount,
            reason=f"Overdue by {loan.days_overdue} days"
        )
        
        self._fines[fine_id] = fine
        
        if loan.member_id not in self._member_fines:
            self._member_fines[loan.member_id] = set()
        self._member_fines[loan.member_id].add(fine_id)
        
        print(f"  [FineCalculator] ⚠️ Fine assessed: ${fine_amount} for loan {loan_id}")
        
        return fine
    
    def pay_fine(self, fine_id: str, amount: float) -> bool:
        """Process fine payment"""
        fine = self._fines.get(fine_id)
        if not fine:
            print(f"  [FineCalculator] ❌ Fine not found: {fine_id}")
            return False
        
        if fine.status == "paid":
            print(f"  [FineCalculator] ❌ Fine already paid")
            return False
        
        if amount < fine.amount:
            print(f"  [FineCalculator] ❌ Insufficient payment: ${amount} < ${fine.amount}")
            return False
        
        fine.pay()
        print(f"  [FineCalculator] ✅ Fine paid: ${fine.amount}")
        
        return True
    
    def waive_fine(self, fine_id: str, reason: str = "Waived") -> bool:
        """Waive a fine"""
        fine = self._fines.get(fine_id)
        if not fine:
            return False
        
        fine.status = "waived"
        fine.paid_date = datetime.now()
        print(f"  [FineCalculator] ✅ Fine waived: ${fine.amount} ({reason})")
        
        return True
    
    def get_member_fines(self, member_id: str, pending_only: bool = True) -> List[Fine]:
        """Get fines for a member"""
        fine_ids = self._member_fines.get(member_id, set())
        fines = []
        
        for fine_id in fine_ids:
            fine = self._fines.get(fine_id)
            if fine:
                if pending_only and fine.status != "pending":
                    continue
                fines.append(fine)
        
        return fines
    
    def get_total_member_fines(self, member_id: str) -> float:
        """Get total pending fines for a member"""
        fines = self.get_member_fines(member_id, pending_only=True)
        return sum(f.amount for f in fines)
    
    def get_fine_stats(self) -> Dict:
        """Get fine statistics"""
        total_fines = len(self._fines)
        pending = len([f for f in self._fines.values() if f.status == "pending"])
        paid = len([f for f in self._fines.values() if f.status == "paid"])
        waived = len([f for f in self._fines.values() if f.status == "waived"])
        
        total_amount = sum(f.amount for f in self._fines.values())
        collected = sum(f.amount for f in self._fines.values() if f.status == "paid")
        outstanding = sum(f.amount for f in self._fines.values() if f.status == "pending")
        
        return {
            'total_fines': total_fines,
            'pending': pending,
            'paid': paid,
            'waived': waived,
            'total_amount': round(total_amount, 2),
            'collected': round(collected, 2),
            'outstanding': round(outstanding, 2)
        }


# ============================================================================
# COMPONENT 5: NOTIFICATION SERVICE
# ============================================================================

class NotificationService:
    """
    Responsible for ALL notification-related operations:
    - Email/SMS templates
    - Overdue notices
    - Reminders
    - Welcome emails
    - Receipts
    """
    
    def __init__(self, member_manager: MemberManager):
        self.member_manager = member_manager
        self._notifications: List[Notification] = []
        print("  [NotificationService] Initialized")
    
    def send_welcome_email(self, member_id: str) -> Optional[Notification]:
        """Send welcome email to new member"""
        member = self.member_manager.get_member(member_id)
        if not member:
            return None
        
        subject = f"Welcome to the Library, {member.name}!"
        message = f"""
        Dear {member.name},
        
        Welcome to our library system! Your membership is now active.
        
        Member ID: {member.member_id}
        Membership Level: {member.membership_level}
        Join Date: {member.join_date.strftime('%Y-%m-%d')}
        
        You can borrow up to {member.max_loans} books at a time.
        
        Happy reading!
        The Library Team
        """
        
        notification = self._create_notification(
            member_id, "welcome", subject, message
        )
        
        print(f"  [NotificationService] 📧 Welcome email sent to {member.email}")
        
        return notification
    
    def send_overdue_notice(self, member_id: str, overdue_loans: List[Loan]) -> Optional[Notification]:
        """Send overdue notice to member"""
        member = self.member_manager.get_member(member_id)
        if not member or not overdue_loans:
            return None
        
        subject = f"Overdue Notice - {len(overdue_loans)} Book(s)"
        
        message = f"""
        Dear {member.name},
        
        The following book(s) are overdue:
        
        """
        
        for loan in overdue_loans:
            book = loan.book_title
            days = loan.days_overdue
            fine = days * 0.50
            message += f"  • {book} - {days} days overdue (${fine:.2f} fine)\n"
        
        message += f"""
        Please return these items as soon as possible to avoid additional fines.
        
        Thank you,
        The Library Team
        """
        
        notification = self._create_notification(
            member_id, "overdue", subject, message
        )
        
        print(f"  [NotificationService] ⚠️ Overdue notice sent to {member.email}")
        
        return notification
    
    def send_due_reminder(self, member_id: str, due_soon: List[Loan]) -> Optional[Notification]:
        """Send reminder for books due soon"""
        member = self.member_manager.get_member(member_id)
        if not member or not due_soon:
            return None
        
        subject = f"Reminder: {len(due_soon)} Book(s) Due Soon"
        
        message = f"""
        Dear {member.name},
        
        The following book(s) are due in 2 days:
        
        """
        
        for loan in due_soon:
            book = loan.book_title
            due = loan.due_date.strftime('%Y-%m-%d')
            message += f"  • {book} - Due: {due}\n"
        
        message += f"""
        You can renew online if you need more time.
        
        Thank you,
        The Library Team
        """
        
        notification = self._create_notification(
            member_id, "reminder", subject, message
        )
        
        print(f"  [NotificationService] 🔔 Reminder sent to {member.email}")
        
        return notification
    
    def send_receipt(self, member_id: str, transaction: Dict) -> Optional[Notification]:
        """Send payment receipt"""
        member = self.member_manager.get_member(member_id)
        if not member:
            return None
        
        subject = f"Payment Receipt - ${transaction.get('amount', 0):.2f}"
        
        message = f"""
        Dear {member.name},
        
        Thank you for your payment!
        
        Amount: ${transaction.get('amount', 0):.2f}
        Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        Transaction ID: {transaction.get('id', 'N/A')}
        
        Your account has been updated.
        
        Thank you,
        The Library Team
        """
        
        notification = self._create_notification(
            member_id, "receipt", subject, message
        )
        
        print(f"  [NotificationService] 🧾 Receipt sent to {member.email}")
        
        return notification
    
    def _create_notification(self, member_id: str, notif_type: str, 
                            subject: str, message: str) -> Notification:
        """Create and store notification"""
        notification = Notification(
            notification_id=f"N{str(uuid.uuid4())[:8].upper()}",
            member_id=member_id,
            type=notif_type,
            subject=subject,
            message=message.strip()
        )
        
        self._notifications.append(notification)
        
        return notification
    
    def get_member_notifications(self, member_id: str) -> List[Notification]:
        """Get notifications for a member"""
        return [n for n in self._notifications if n.member_id == member_id]
    
    def get_all_notifications(self) -> List[Notification]:
        """Get all notifications"""
        return self._notifications


# ============================================================================
# COMPONENT 6: REPORTING ENGINE
# ============================================================================

class ReportingEngine:
    """
    Responsible for ALL reporting-related operations:
    - Usage statistics
    - Financial reports
    - Popular books
    - Member activity
    - System health
    """
    
    def __init__(self, book_manager: BookManager, member_manager: MemberManager,
                 loan_manager: LoanManager, fine_calculator: FineCalculator):
        self.book_manager = book_manager
        self.member_manager = member_manager
        self.loan_manager = loan_manager
        self.fine_calculator = fine_calculator
        print("  [ReportingEngine] Initialized")
    
    def generate_inventory_report(self) -> Dict:
        """Generate book inventory report"""
        books = self.book_manager.get_all_books()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'report_type': 'Inventory',
            'total_unique_titles': len(books),
            'total_copies': sum(b.total_copies for b in books),
            'available_copies': sum(b.available_copies for b in books),
            'checked_out': sum(b.total_copies - b.available_copies for b in books),
            'books_by_year': {},
            'books_by_author': {}
        }
        
        # Group by year
        for book in books:
            year = book.year
            report['books_by_year'][year] = report['books_by_year'].get(year, 0) + 1
        
        # Group by author (top 10)
        author_counts = {}
        for book in books:
            author_counts[book.author] = author_counts.get(book.author, 0) + 1
        
        top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        report['books_by_author'] = dict(top_authors)
        
        return report
    
    def generate_member_activity_report(self) -> Dict:
        """Generate member activity report"""
        members = self.member_manager.get_all_members()
        active_loans = self.loan_manager.get_active_loans()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'report_type': 'Member Activity',
            'total_members': len(members),
            'active_members': len([m for m in members if m.active]),
            'members_with_loans': len(set(l.member_id for l in active_loans)),
            'total_active_loans': len(active_loans),
            'avg_loans_per_member': len(active_loans) / max(len(members), 1),
            'membership_breakdown': {}
        }
        
        # Membership level breakdown
        for member in members:
            level = member.membership_level
            if level not in report['membership_breakdown']:
                report['membership_breakdown'][level] = {
                    'count': 0,
                    'total_loans': 0
                }
            report['membership_breakdown'][level]['count'] += 1
            report['membership_breakdown'][level]['total_loans'] += member.current_loans
        
        return report
    
    def generate_popular_books_report(self, limit: int = 10) -> Dict:
        """Generate popular books report"""
        all_loans = list(self.loan_manager._loans.values())
        
        # Count loans per book
        loan_counts = {}
        for loan in all_loans:
            isbn = loan.isbn
            loan_counts[isbn] = loan_counts.get(isbn, 0) + 1
        
        # Sort by popularity
        popular_isbns = sorted(loan_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        popular_books = []
        for isbn, count in popular_isbns:
            book = self.book_manager.get_book(isbn)
            if book:
                popular_books.append({
                    'title': book.title,
                    'author': book.author,
                    'isbn': isbn,
                    'times_borrowed': count,
                    'available': book.available_copies
                })
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'report_type': 'Popular Books',
            'top_books': popular_books,
            'total_borrows': len(all_loans)
        }
        
        return report
    
    def generate_financial_report(self) -> Dict:
        """Generate financial report"""
        fine_stats = self.fine_calculator.get_fine_stats()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'report_type': 'Financial',
            'fine_statistics': fine_stats,
            'revenue': {
                'total_collected': fine_stats['collected'],
                'outstanding': fine_stats['outstanding'],
                'waived': sum(f.amount for f in self.fine_calculator._fines.values() 
                            if f.status == 'waived')
            }
        }
        
        return report
    
    def generate_overdue_report(self) -> Dict:
        """Generate overdue loans report"""
        overdue = self.loan_manager.get_overdue_loans()
        
        overdue_details = []
        for loan in overdue:
            member = self.member_manager.get_member(loan.member_id)
            fine = self.fine_calculator.calculate_fine(loan.loan_id)
            overdue_details.append({
                'loan_id': loan.loan_id,
                'book_title': loan.book_title,
                'member_name': member.name if member else 'Unknown',
                'member_email': member.email if member else 'Unknown',
                'due_date': loan.due_date.isoformat(),
                'days_overdue': loan.days_overdue,
                'fine': fine
            })
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'report_type': 'Overdue Items',
            'total_overdue': len(overdue),
            'overdue_items': overdue_details,
            'total_fines': sum(d['fine'] for d in overdue_details)
        }
        
        return report
    
    def generate_system_health_report(self) -> Dict:
        """Generate system health report"""
        book_stats = self.book_manager.get_inventory_stats()
        member_stats = self.member_manager.get_member_stats()
        loan_stats = self.loan_manager.get_loan_stats()
        fine_stats = self.fine_calculator.get_fine_stats()
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'report_type': 'System Health',
            'components': {
                'BookManager': {'status': 'healthy', 'statistics': book_stats},
                'MemberManager': {'status': 'healthy', 'statistics': member_stats},
                'LoanManager': {'status': 'healthy', 'statistics': loan_stats},
                'FineCalculator': {'status': 'healthy', 'statistics': fine_stats},
                'NotificationService': {'status': 'healthy'},
                'ReportingEngine': {'status': 'healthy'}
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return report


# ============================================================================
# ORCHESTRATOR: LIBRARY SYSTEM (COMPOSES ALL COMPONENTS)
# ============================================================================

class LibrarySystem:
    """
    Orchestrator that composes all independent components.
    
    This class DOES NOT contain business logic - it only:
    1. Initializes components with dependency injection
    2. Provides a unified facade for clients
    3. Delegates all operations to specialized components
    """
    
    def __init__(self):
        # Initialize components with proper dependencies
        self.book_manager = BookManager()
        self.member_manager = MemberManager()
        self.loan_manager = LoanManager(self.book_manager, self.member_manager)
        self.fine_calculator = FineCalculator(self.loan_manager, self.member_manager)
        self.notification_service = NotificationService(self.member_manager)
        self.reporting_engine = ReportingEngine(
            self.book_manager, 
            self.member_manager, 
            self.loan_manager, 
            self.fine_calculator
        )
        
        print("\n" + "="*60)
        print("📚 LIBRARY SYSTEM ITIALIZED")
        print("="*60)
        print(f"Components: BookManager, MemberManager, LoanManager,")
        print(f"           FineCalculator, NotificationService, ReportingEngine")
        print("="*60)
    
    # ======== Book Operations (Delegated) ========
    def add_book(self, isbn: str, title: str, author: str, year: int, copies: int = 1):
        return self.book_manager.add_book(isbn, title, author, year, copies)
    
    def remove_book(self, isbn: str):
        return self.book_manager.remove_book(isbn)
    
    def get_book(self, isbn: str):
        return self.book_manager.get_book(isbn)
    
    def find_books_by_title(self, title: str):
        return self.book_manager.find_books_by_title(title)
    
    def find_books_by_author(self, author: str):
        return self.book_manager.find_books_by_author(author)
    
    def is_book_available(self, isbn: str):
        return self.book_manager.is_available(isbn)
    
    # ======== Member Operations (Delegated) ========
    def register_member(self, name: str, email: str, phone: str, membership_level: str = "standard"):
        return self.member_manager.register_member(name, email, phone, membership_level)
    
    def get_member(self, member_id: str):
        return self.member_manager.get_member(member_id)
    
    def update_member(self, member_id: str, **kwargs):
        return self.member_manager.update_member(member_id, **kwargs)
    
    def deactivate_member(self, member_id: str):
        return self.member_manager.deactivate_member(member_id)
    
    def activate_member(self, member_id: str):
        return self.member_manager.activate_member(member_id)
    
    # ======== Loan Operations (Delegated) ========
    def borrow_book(self, member_id: str, isbn: str):
        loan = self.loan_manager.borrow_book(member_id, isbn)
        if loan:
            # Auto-assess fine if overdue (though just borrowed, so not overdue)
            pass
        return loan
    
    def return_book(self, loan_id: str):
        loan = self.loan_manager.return_book(loan_id)
        if loan and loan.is_overdue:
            # Assess fine for overdue return
            self.fine_calculator.assess_fine(loan_id)
        return loan
    
    def renew_loan(self, loan_id: str, days: int = 7):
        return self.loan_manager.renew_loan(loan_id, days)
    
    def get_member_loans(self, member_id: str, active_only: bool = True):
        return self.loan_manager.get_member_loans(member_id, active_only)
    
    def get_overdue_loans(self):
        return self.loan_manager.get_overdue_loans()
    
    # ======== Fine Operations (Delegated) ========
    def calculate_fine(self, loan_id: str):
        return self.fine_calculator.calculate_fine(loan_id)
    
    def assess_fine(self, loan_id: str):
        return self.fine_calculator.assess_fine(loan_id)
    
    def pay_fine(self, fine_id: str, amount: float):
        result = self.fine_calculator.pay_fine(fine_id, amount)
        if result:
            # Send receipt notification
            fine = self.fine_calculator._fines.get(fine_id)
            if fine:
                self.notification_service.send_receipt(
                    fine.member_id, 
                    {'id': fine_id, 'amount': amount}
                )
        return result
    
    def waive_fine(self, fine_id: str, reason: str = "Waived"):
        return self.fine_calculator.waive_fine(fine_id, reason)
    
    def get_member_fines(self, member_id: str, pending_only: bool = True):
        return self.fine_calculator.get_member_fines(member_id, pending_only)
    
    # ======== Notification Operations (Delegated) ========
    def send_welcome_email(self, member_id: str):
        return self.notification_service.send_welcome_email(member_id)
    
    def send_overdue_notices(self):
        """Send overdue notices to all members with overdue books"""
        overdue_loans = self.loan_manager.get_overdue_loans()
        
        # Group by member
        member_overdue = {}
        for loan in overdue_loans:
            if loan.member_id not in member_overdue:
                member_overdue[loan.member_id] = []
            member_overdue[loan.member_id].append(loan)
        
        # Send notice to each member
        for member_id, loans in member_overdue.items():
            self.notification_service.send_overdue_notice(member_id, loans)
    
    def send_due_reminders(self):
        """Send reminders for books due in 2 days"""
        active_loans = self.loan_manager.get_active_loans()
        due_soon = []
        
        for loan in active_loans:
            days_until_due = (loan.due_date - datetime.now()).days
            if 0 <= days_until_due <= 2:
                due_soon.append(loan)
        
        # Group by member
        member_due = {}
        for loan in due_soon:
            if loan.member_id not in member_due:
                member_due[loan.member_id] = []
            member_due[loan.member_id].append(loan)
        
        # Send reminder to each member
        for member_id, loans in member_due.items():
            self.notification_service.send_due_reminder(member_id, loans)
    
    # ======== Report Operations (Delegated) ========
    def generate_inventory_report(self):
        return self.reporting_engine.generate_inventory_report()
    
    def generate_member_activity_report(self):
        return self.reporting_engine.generate_member_activity_report()
    
    def generate_popular_books_report(self, limit: int = 10):
        return self.reporting_engine.generate_popular_books_report(limit)
    
    def generate_financial_report(self):
        return self.reporting_engine.generate_financial_report()
    
    def generate_overdue_report(self):
        return self.reporting_engine.generate_overdue_report()
    
    def generate_system_health_report(self):
        return self.reporting_engine.generate_system_health_report()


# ============================================================================
# COMPONENT DIAGRAM
# ============================================================================

def display_component_diagram():
    """Display ASCII component diagram showing separation of concerns"""
    
    diagram = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    LIBRARY SYSTEM - COMPONENT DIAGRAM                        ║
║                        Separation of Concerns Architecture                   ║
╚══â═══════════════════════════════════════════════════════════╝

                                    ┌─────────────────┐
                                    │   LIBRARY      │
                                    │   ORCHESTRATOR │
                                    │    (Facade)    │
                                    └─────â─┘
            ┌───────────────────────────────┼───────────────────────────────┐
            │                               │                               │
            ▼                               ▼                               ▼
    ┌───────────────┐              ┌───────────────┐      ┌───────────────┐
    │ BOOK MANAGER  │              │ MEMBER MANAGER│              │  LOAN MANAGER │
    │               │              │               │              │               │
    │ • Catalog     │              │ • Registration│              │ • Borrowing   │
    │ • Inventory   │◄────────────►│ • Profiles    │◄────────────►│ • Returns     │
    │       │              │ • Eligibility │              │ • Renewals    │
    │ • Availability│              │ • Status      │              │ • Due dates   │
    └───────────────┘              └───────────────┘              └───────────────┘
            ▲                               ▲                               ▲
            │                               │                               │
            │                               │                               │
            ▼                               ▼                               ▼
    ┌───────────────┐              ┌───────────────┐              ┌───────────────┐
    │ FINE          │              │ NOTIFICATION  │              │  REPORTING    │
    │ CALCULATOR    │          │   SERVICE     │              │    ENGINE     │
    │               │              │               │              │               │
    │ • Calculation │              │ • Welcome     │              │ • Inventory   │
    │ • Assessment  │              │ • Overdue     │              │ • Activity    │
    │ • Payments    │              │ • Reminders   │              │ • Popular     │
    │ • Waivers     │              │ • Recs    │              │ • Financial   │
    └───────────────┘              └───────────────┘              └───────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LEGEND:
────►  Dependency/Data ────  Composition/Orchestration
┌───┐  Independent Component with Single Responsibility
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    print(diagram)


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demonstrate_modular_library():
    """Demonstrate the modular library system"""
    
    print("\n" + "="*80)
    print("EXERCISE 2.1: Break Down a Monolithic System 🟢")
    print("="*80)
    
    # Display component diagram
    display_component_diagram()
    
    # Initialize library system
    print("\n🚀 INITIALIZING MODULAR LIBRARY SYSTEM")
    print("="*80)
    library = LibrarySystem()
    
    # ======== SCENARIO 1: Add Books ========
    print("\n📚 SCENARAdding Books to Catalog")
    print("-"*60)
    
    library.add_book("978-0451524935", "1984", "George Orwell", 1949, 3)
    library.add_book("978-0061120084", "To Kill a Mockingbird", "Harper Lee", 1960, 2)
    library.add_book("978-0141187761", "The Great Gatsby", "F. Scott Fitzgerald", 1925, 2)
    library.add_book("978-0743273565", "The Great Gatsby", "F. Scott Fitzgerald", 1925, 1)  # Add copies
    library.add_book("978-1503280786", "Moby Dick", "Herman Melville", 1851, 1)
    
    # ======== SCENARIO 2: Register Members ========
    print("\n👥 SCENARIO 2: Registering Members")
    print("-"*60)
    
    alice = library.register_member("Alice Johnson", "alice@email.com", "555-0101", "premium")
    bob = library.register_member("Bob Smith", "bob@email.com", "555-0102", "standard")
    charlie = library.register_member("Charlie Brown", "charlie@email.com", "555-0103", "student")
    
    # Send welcome emails
    library.send_welcome_email(alice.member_id)
    library.send_welcome_email(bob.member_id)   
    # ======== SCENARIO 3: Borrowing Books ========
    print("\n📖 SCENARIO 3: Borrowing Books")
    print("-"*60)
    
    # Alice borrows 1984
    loan1 = library.borrow_book(alice.member_id, "978-0451524935")
    
    # Bob borrows To Kill a Mockingbird
    loan2 = library.borrow_book(bob.member_id, "978-0061120084")
    
    # Charlie borrows The Great Gatsby
    loan3 = library.borrow_book(charlie.member_id, "978-0141187761")
    
    # Try to borrow unavailable book
    library.borrow_book(bob.mber_id, "978-0451524935")  # Should fail (only 1 left, Alice has it)
    
    # ======== SCENARIO 4: Check Member Status ========
    print("\n📊 SCENARIO 4: Member Status")
    print("-"*60)
    
    alice_status = library.get_member(alice.member_id)
    print(f"\n  Member: {alice_status.name}")
    print(f"  Active Loans: {alice_status.current_loans}/{alice_status.max_loans}")
    
    # ======== SCENARIO 5: Return Book with Fine ========
    print("\n💰 SCENARIO 5: Return Book with Fine Calculation"  print("-"*60)
    
    # Simulate overdue by modifying due date
    if loan1:
        loan1.due_date = datetime.now() - timedelta(days=5)
        print(f"\n  [Simulation] Loan {loan1.loan_id} is now 5 days overdue")
    
    # Return book - should assess fine
    library.return_book(loan1.loan_id)
    
    # Check fines for Alice
    alice_fines = library.get_member_fines(alice.member_id)
    print(f"\n  Alice's pending fines: ${sum(f.amount for f in alice_fines):.2f}")
    
    # Pay fine
    if alice_fines:
        library.pay_fine(alice_fines[0].fine_id, alice_fines[0].amount)
    
    # ======== SCENARIO 6: Renew Loan ========
    print("\n🔄 SCENARIO 6: Renew Loan")
    print("-"*60)
    
    if loan2:
        library.renew_loan(loan2.loan_id, days=7)
    
    # ======== SCENARIO 7: Send Notifications ========
    print("\n📧 SCENARIO 7: Automated Notifications")
    print("-"*60)
    
    # Send overdue notices
    library.send_overdue_notices()
    
    # Send due reminders
    library.send_due_rinders()
    
    # ======== SCENARIO 8: Generate Reports ========
    print("\n📑 SCENARIO 8: Generating Reports")
    print("-"*60)
    
    # Inventory Report
    print("\n  📊 INVENTORY REPORT:")
    inventory = library.generate_inventory_report()
    print(f"     Total Titles: {inventory['total_unique_titles']}")
    print(f"     Total Copies: {inventory['total_copies']}")
    print(f"     Available: {inventory['available_copies']}")
    print(f"     Checked Out: {inventory['checked_out']}")
    
  Popular Books Report
    print("\n  🔥 POPULAR BOOKS:")
    popular = library.generate_popular_books_report(limit=3)
    for book in popular['top_books']:
        print(f"     • {book['title']} - {book['times_borrowed']} borrows")
    
    # Financial Report
    print("\n  💰 FINANCIAL REPORT:")
    financial = library.generate_financial_report()
    print(f"     Total Fines Collected: ${financial['revenue']['total_collected']:.2f}")
    print(f"     Outstanding Fines: ${financial['revenue']['outstan:.2f}")
    
    # System Health Report
    print("\n  🏥 SYSTEM HEALTH:")
    health = library.generate_system_health_report()
    for component, data in health['components'].items():
        print(f"     • {component}: {data['status']}")
    
    # ======== DEMONSTRATE INDEPENDENT TESTING ========
    print("\n" + "="*80)
    print("🧪 DEMONSTRATION: Independent Component Testing")
    print("="*80)
    print("""
    Each component can be tested in isolation:
    
    ✅ BookManager test:
        bManager()
        bm.add_book("123", "Test Book", "Author", 2024)
        assert bm.is_available("123") == True
    
    ✅ MemberManager test:
        mm = MemberManager()
        member = mm.register_member("Test User", "test@test.com", "555-0000")
        assert mm.can_borrow(member.member_id) == True
    
    ✅ LoanManager test (with mocks):
        mock_bm = MockBookManager()
        mock_mm = MockMemberManager()
        lm = LoanManager(mock_bm, mock_mm)
        loan = lm.borrow_book("M001", "123")     assert loan is not None
    
    ✅ FineCalculator test:
        fc = FineCalculator(loan_manager, member_manager)
        fine = fc.calculate_fine(loan_id)
        assert fine >= 0
    
    ✅ NotificationService test:
        ns = NotificationService(member_manager)
        notif = ns.send_welcome_email("M001")
        assert notif.type == "welcome"
    
    ✅ ReportingEngine test:
        re = ReportingEngine(bm, mm, lm, fc)
        report = re.generate_inventory_report()
        assert report['_type'] == 'Inventory'
    """)


def main():
    """Main entry point"""
    demonstrate_modular_library()
    
    print("\n" + "="*80)
    print("📌 SUMMARY: Separation of Concerns Achieved")
    print("="*80)
    print("""
    ┌──────────────────────────────┬─────────────────────────────────────────┐
    │ BEFORE (Monolithic)          │ AFTER (Modular)              │
    ├──────────────────────────────┼─────────────────────────────────────────┤
    │ • 1 class, 200+ lines       │ • 7 classes, focused responsibilities  │
    │ • All concerns mixed        │ • Each component has ONE job           │
    │ • Cannot test separately    │ • Each component testable in isolation │
    │nges risk everything   │ • Changes isolated to one component    │
    │ • Hard to parallelize work  │ • Multiple devs work simultaneously    │
    │ • No clear boundaries       │ • Clear interfaces between components  │
    │ • Hidden dependencies       │ • Explicit dependency injection        │
    │ • Rigid, hard to extend     │ • Flexible, easy to extend            │
    └────────────────────────────â─────────────────────────────────┘
    
    🎯 KEY ACHIEVEMENTS:
    
    1. IDENTIFIED 6 DISTINCT COMPONENTS:
       • BookManager - Book catalog and inventory
       • MemberManager - Member registry and profiles
       • LoanManager - Borrowing, returns, renewals
       • FineCalculator - Fine calculation and payments
       • NotificationService - Member communications
       • ReportingEngine - Data aggregation and rep
    
    2. CREATED CLEAN ORCHESTRATOR:
       • LibrarySystem composes components
       • No business logic - pure delegation
       • Dependency injection throughout
    
    3. ENABLED INDEPENDENT TESTING:
       • Each component can be mocked
       • Unit tests without database
       • Fast, reliable test suites
    
    4. ACHIEVED SINGLE RESPONSIBILITY:
       • Each class has ONE reason to change
       • Changes propagate minimally
       • System is now maintainable
    """)

f __name__ == "__main__":
    main()
