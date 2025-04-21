from Observer import Observer
from Book import Book
from datetime import datetime, timedelta
from Exceptions import *

# --- User Class (Enhanced Observer) ---
class User(Observer):
    def __init__(self, user_id, name, email):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.fines = 0.0
        self.checked_out_books = []

    def get_user_id(self): return self.user_id
    def get_name(self): return self.name
    def get_email(self): return self.email
    def get_fines(self): return self.fines

    def add_fine(self, amount):
        if amount > 0:
            self.fines += amount
            print(f"Fine of ${amount:.2f} added to {self.name}. Total fines: ${self.fines:.2f}")

    def pay_fine(self, amount):
        if amount <= 0:
            print("Payment amount must be positive.")
            return
        paid_amount = min(amount, self.fines)
        self.fines -= paid_amount
        print(f"{self.name} paid ${paid_amount:.2f}. Remaining fines: ${self.fines:.2f}")

    def _actual_checkout_book(self, book: Book, library):
        """Internal logic for checking out a book."""
        due_date = datetime.now().date() + timedelta(days=library.checkout_duration_days)
        try:
            # The book object itself validates if it can be checked out by this user
            book.checkout(self, due_date)
            self.checked_out_books.append(book)
            print(f"{self.name} checked out '{book.get_title()}'. Due: {due_date}")
            return True
        except BookUnavailableError as e:
            print(f"Checkout failed for {self.name}: {e}")
            # raise # Re-raise if command invoker should handle it
            return False # Or return False for command invoker logging

    def _actual_return_book(self, book: Book, library):
        """Internal logic for returning a book."""
        if book not in self.checked_out_books:
            raise NotCheckedOutError(f"{self.name} did not check out '{book.get_title()}'.")

        # Calculate fines *before* changing status/detaching user
        if book.due_date and datetime.now().date() > book.due_date:
            overdue_days = (datetime.now().date() - book.due_date).days
            fine_amount = overdue_days * library.fine_rate_per_day
            self.add_fine(fine_amount)

        try:
            # Book handles status change and waitlist processing
            book.return_book()
            self.checked_out_books.remove(book)
            print(f"{self.name} returned '{book.get_title()}'.")
            return True
        except LibraryError as e: # Catch potential errors during return process
            print(f"Return failed for {self.name}: {e}")
            return False

    def _actual_reserve_book(self, book: Book):
        """Internal logic for reserving a book."""
        if not book._can_reserve(self):
             raise BookUnavailableError(f"'{book.get_title()}' cannot be reserved by {self.name}. Status: {book.get_status()}")

        if book.add_to_waitlist(self):
            return True
        else:
            print(f"{self.name} is already on the waitlist or borrowing '{book.get_title()}'.")
            return False

    def update(self, subject, message):
        """Receives notification from observed subjects (Books)."""
        print(f"Notification for User {self.name}: {message}")
        # Example: If book is now reserved for this user
        if isinstance(subject, Book) and subject.get_status() == "reserved" and subject.borrower == self:
             print(f"  Action required: '{subject.get_title()}' is ready for pickup.")

