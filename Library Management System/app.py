import abc
from datetime import datetime, timedelta
from Exceptions import *
from Book import *
from Command import *
from Factory import *


# --- Singleton Library (Added Config) ---
class Library:
    _instance = None

    @staticmethod
    def get_instance():
        if Library._instance is None:
            Library()
        return Library._instance

    def __init__(self):
        if Library._instance is not None:
            raise Exception("This class is a singleton! Use get_instance().")
        else:
            self._catalog = BookCollection("Main Catalog")
            self.user_list = []
            self.librarian_list = [] # Store librarians separately now
            self.command_invoker = CommandInvoker()
            # Library configuration
            self.fine_rate_per_day = 0.50 # Example: $0.50 per day
            self.checkout_duration_days = 14
            Library._instance = self

    def get_catalog(self): return self._catalog
    def find_librarian(self, staff_id): # Specific finder for librarian
        for lib in self.librarian_list:
            if lib.get_staff_id() == staff_id:
                return lib
        return None

    def find_user(self, user_id): # Finds only regular users
        for user in self.user_list:
            if user.get_user_id() == user_id:
                return user
        return None

    def get_all_books(self):
        return self._catalog.get_books()

    def get_available_books(self):
        # Only books explicitly marked 'available' or 'reserved' (but maybe show differently)
        return [book for book in self.get_all_books() if book.get_status() == "available"]

    def find_book(self, isbn):
        for book in self.get_all_books():
             if book.get_isbn() == isbn:
                 return book
        raise BookNotFoundError(f"Book with ISBN {isbn} not found.")


    def search_books(self, criteria):
        results = []
        all_books = self.get_all_books()
        criteria_lower = criteria.lower()
        for book in all_books:
            # Exclude archived/lost/damaged from general search? Optional.
            # if book.get_status() in ["lost", "damaged", "archived"]: continue
            if criteria_lower in book.get_title().lower() or \
               criteria_lower in book.get_author().lower() or \
               criteria_lower == book.get_isbn():
                results.append(book)
        return results

    def notify_users(self):
        today = datetime.now().date()
        print("\n--- Sending Notifications ---")
        for user in self.user_list:
            # Notify about overdue books
            for book in user.checked_out_books:
                if book.due_date and book.due_date < today:
                    print(f"  OVERDUE Notice to {user.get_name()}: Book '{book.get_title()}' was due on {book.due_date}!")
            # Notify about pending fines
            if user.get_fines() > 0:
                 print(f"  FINE Notice to {user.get_name()}: You have outstanding fines of ${user.get_fines():.2f}.")
            # Notify about reserved books ready for pickup (via Observer update now)

        print("--- Notifications Sent ---")


    def display_catalog(self):
        print("\n--- Library Catalog ---")
        self._catalog.display_info()
        print("--- End Catalog ---\n")

    def get_transaction_history(self):
        return self.command_invoker._history


# --- Enhanced Example Usage ---

# Singleton Library instance
library = Library.get_instance()
invoker = library.command_invoker

# Factory to create people
factory = PersonFactory()
try:
    user1 = factory.create_person("user", "U001", "Alice", "alice@example.com")
    user2 = factory.create_person("user", "U002", "Charlie", "charlie@example.com")
    librarian1 = factory.create_person("librarian", "L001", "Bob", "bob@example.com")
except ValueError as e:
    print(e)
    exit()

# Register Librarian with Library
library.librarian_list.append(librarian1)

# Librarian manages users
invoker.execute_command(ManageUserCommand(librarian1, library, user1, 'add'))
invoker.execute_command(ManageUserCommand(librarian1, library, user2, 'add'))

# Create books and collections
book1 = Book("The Great Gatsby", "F. Scott Fitzgerald", "1234567890")
book2 = Book("To Kill a Mockingbird", "Harper Lee", "0987654321")
book3 = Book("1984", "George Orwell", "1122334455")
fiction_collection = BookCollection("Fiction")

# Librarian adds items
invoker.execute_command(AddItemCommand(librarian1, library, fiction_collection))
invoker.execute_command(AddItemCommand(librarian1, library, book1, fiction_collection))
invoker.execute_command(AddItemCommand(librarian1, library, book2)) # Add to root
invoker.execute_command(AddItemCommand(librarian1, library, book3, fiction_collection))

library.display_catalog()

print("\n--- User Actions & Error Handling ---")

# Alice checks out Gatsby
print("Alice checks out Gatsby...")
invoker.execute_command(CheckoutBookCommand(user1, book1, library))

# Charlie tries to check out Gatsby (should fail)
print("\nCharlie tries to check out Gatsby...")
invoker.execute_command(CheckoutBookCommand(user2, book1, library))

# Charlie reserves Gatsby (should succeed)
print("\nCharlie reserves Gatsby...")
invoker.execute_command(ReserveBookCommand(user2, book1))

# Alice tries to reserve Gatsby (should fail - she has it)
print("\nAlice tries to reserve Gatsby...")
invoker.execute_command(ReserveBookCommand(user1, book1))

# Alice returns Gatsby (simulate overdue)
print("\nAlice returns Gatsby (overdue)...")
book1.due_date = datetime.now().date() - timedelta(days=3) # Make it 3 days overdue
invoker.execute_command(ReturnBookCommand(user1, book1, library))
# Note: Observer pattern notified Charlie about reservation earlier via update method.

# Check Alice's fines
print(f"Alice's fines: ${user1.get_fines():.2f}")
user1.pay_fine(1.0) # Pay part of the fine

# Charlie checks out Gatsby (was reserved for him)
print("\nCharlie checks out Gatsby...")
invoker.execute_command(CheckoutBookCommand(user2, book1, library))

# Librarian marks '1984' as 'lost'
print("\nLibrarian marks '1984' as lost...")
invoker.execute_command(UpdateBookStatusCommand(librarian1, book3, "lost"))

# Try to check out the lost book (should fail)
print("\nAlice tries to check out '1984'...")
invoker.execute_command(CheckoutBookCommand(user1, book3, library))

library.display_catalog()

# Generate report and show transactions
librarian1.generate_report(library)

print("\n--- Transaction History ---")
for transaction in library.get_transaction_history():
    print(transaction.get_details())