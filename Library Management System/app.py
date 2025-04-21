import abc
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


# --- Librarian Class (Separate, Not Inheriting User) ---
class Librarian:
    def __init__(self, staff_id, name, email):
        self.staff_id = staff_id # Use staff_id instead of user_id
        self.name = name
        self.email = email

    def get_staff_id(self): return self.staff_id
    def get_name(self): return self.name
    def get_email(self): return self.email

    def _actual_add_item(self, library, item: LibraryItem, collection: BookCollection = None):
        target_collection = collection if collection else library.get_catalog()
        try:
            target_collection.add(item)
            print(f"Librarian {self.name} added '{getattr(item, 'name', item.title)}' to {'collection ' + target_collection.name if target_collection != library.get_catalog() else 'main catalog'}.")
            return True
        except InvalidOperationError as e:
            print(f"Add item failed: {e}")
            return False

    def _actual_remove_item(self, library, item: LibraryItem, collection: BookCollection = None):
        target_collection = collection if collection else library.get_catalog()
        try:
            target_collection.remove(item)
            print(f"Librarian {self.name} removed '{getattr(item, 'name', item.title)}' from {'collection ' + target_collection.name if target_collection != library.get_catalog() else 'main catalog'}.")
            return True
        except (BookNotFoundError, InvalidOperationError) as e:
             print(f"Remove item failed: {e}")
             return False


    def _actual_manage_user(self, library, user: User, action: str):
        if action == 'add':
            if user not in library.user_list:
                library.user_list.append(user)
                print(f"Librarian {self.name} registered user {user.get_name()}.")
                return True
            else:
                print(f"User {user.get_name()} is already registered.")
                return False
        elif action == 'remove':
             if user in library.user_list:
                library.user_list.remove(user)
                # Consider implications: outstanding checkouts, fines?
                print(f"Librarian {self.name} removed user {user.get_name()}.")
                return True
             else:
                 raise UserNotFoundError(f"User {user.get_name()} not found.")
        else:
            print(f"Invalid user management action: {action}")
            return False

    def _actual_update_book_status(self, book: Book, new_status: str):
        try:
            book.update_status(new_status) # Book handles internal logic & notifications
            print(f"Librarian {self.name} updated '{book.get_title()}' status to {new_status}.")
            return True
        except (ValueError, LibraryError) as e:
            print(f"Update status failed: {e}")
            return False

    def generate_report(self, library):
        print("\n--- Library Report ---")
        print(f"Total Users Registered: {len(library.user_list)}")
        all_books = library.get_all_books()
        print(f"Total Books in Catalog: {len(all_books)}")
        status_counts = {status: 0 for status in Book.VALID_STATUSES}
        total_fines = sum(user.get_fines() for user in library.user_list)
        active_waitlists = 0
        for book in all_books:
            status_counts[book.get_status()] += 1
            if book.waitlist: active_waitlists += 1

        for status, count in status_counts.items():
            print(f"  Books - {status.capitalize()}: {count}")
        print(f"Active Waitlists: {active_waitlists}")
        print(f"Total Outstanding Fines: ${total_fines:.2f}")
        print("--- End Report ---\n")


# --- Factory Pattern (Updated for Librarian) ---
class PersonFactory: # Renamed from UserFactory
    @staticmethod
    def create_person(person_type: str, id: str, name: str, email: str):
        if person_type.lower() == 'librarian':
            # Expects staff_id for librarian
            return Librarian(staff_id=id, name=name, email=email)
        elif person_type.lower() == 'user':
            # Expects user_id for user
            return User(user_id=id, name=name, email=email)
        else:
            raise ValueError(f"Unknown person type: {person_type}")


# --- Command Pattern (Added Reserve, UpdateStatus) ---
class Command(abc.ABC):
    @abc.abstractmethod
    def execute(self):
        """Executes the command. Should return True/False or raise Exception on failure."""
        pass

class CheckoutBookCommand(Command):
    def __init__(self, user: User, book: Book, library):
        self.user = user
        self.book = book
        self.library = library # Needed for checkout duration, etc.

    def execute(self):
        # Logic moved to User, raises exceptions on failure
        return self.user._actual_checkout_book(self.book, self.library)

class ReturnBookCommand(Command):
    def __init__(self, user: User, book: Book, library):
        self.user = user
        self.book = book
        self.library = library # Needed for fine calculation

    def execute(self):
        # Logic moved to User, raises exceptions on failure
        return self.user._actual_return_book(self.book, self.library)

class ReserveBookCommand(Command):
    def __init__(self, user: User, book: Book):
        self.user = user
        self.book = book

    def execute(self):
        # Logic moved to User, raises exceptions on failure
        return self.user._actual_reserve_book(self.book)

class AddItemCommand(Command):
    def __init__(self, librarian: Librarian, library, item: LibraryItem, collection: BookCollection = None):
        self.librarian = librarian
        self.library = library
        self.item = item
        self.collection = collection

    def execute(self):
        # Logic in Librarian
        return self.librarian._actual_add_item(self.library, self.item, self.collection)

class RemoveItemCommand(Command):
     def __init__(self, librarian: Librarian, library, item: LibraryItem, collection: BookCollection = None):
        self.librarian = librarian
        self.library = library
        self.item = item
        self.collection = collection

     def execute(self):
         # Logic in Librarian
         return self.librarian._actual_remove_item(self.library, self.item, self.collection)

class ManageUserCommand(Command):
    def __init__(self, librarian: Librarian, library, user: User, action: str):
        self.librarian = librarian
        self.library = library
        self.user = user
        self.action = action

    def execute(self):
        # Logic in Librarian
        return self.librarian._actual_manage_user(self.library, self.user, self.action)

class UpdateBookStatusCommand(Command):
    def __init__(self, librarian: Librarian, book: Book, new_status: str):
        self.librarian = librarian
        self.book = book
        self.new_status = new_status

    def execute(self):
        # Logic in Librarian
        return self.librarian._actual_update_book_status(self.book, self.new_status)


# --- Transaction Class (Slightly Enhanced) ---
class Transaction:
    _id_counter = 0
    def __init__(self, actor_id, target_id, transaction_type, success: bool, details: str = ""):
        Transaction._id_counter += 1
        self.transaction_id = Transaction._id_counter
        self.actor_id = actor_id # User ID or Staff ID performing action
        self.target_id = target_id # ISBN, User ID being managed, Collection Name etc.
        self.transaction_date = datetime.now()
        self.transaction_type = transaction_type
        self.success = success
        self.details = details # Optional message (e.g., error message)

    def get_details(self):
        status = "Success" if self.success else "Failed"
        detail_msg = f" ({self.details})" if self.details else ""
        return (f"ID: {self.transaction_id}, Date: {self.transaction_date.strftime('%Y-%m-%d %H:%M')}, "
                f"Actor: {self.actor_id}, Target: {self.target_id}, Type: {self.transaction_type}, Status: {status}{detail_msg}")

# --- Command Invoker (Handles Exceptions) ---
class CommandInvoker:
    def __init__(self):
        self._history = []

    def execute_command(self, command: Command):
        actor = None
        target = None
        trans_type = "unknown"
        success = False
        error_details = ""

        # Determine actors/targets beforehand for logging
        if hasattr(command, 'user'): actor = command.user.get_user_id()
        if hasattr(command, 'librarian'): actor = command.librarian.get_staff_id()

        if isinstance(command, (CheckoutBookCommand, ReturnBookCommand, ReserveBookCommand, UpdateBookStatusCommand)):
            target = command.book.get_isbn()
            if isinstance(command, CheckoutBookCommand): trans_type = "checkout"
            elif isinstance(command, ReturnBookCommand): trans_type = "return"
            elif isinstance(command, ReserveBookCommand): trans_type = "reserve"
            elif isinstance(command, UpdateBookStatusCommand): trans_type = f"update_status_{command.new_status}"
        elif isinstance(command, (AddItemCommand, RemoveItemCommand)):
            target = getattr(command.item, 'name', getattr(command.item, 'title', 'Unknown Item'))
            trans_type = "add_item" if isinstance(command, AddItemCommand) else "remove_item"
        elif isinstance(command, ManageUserCommand):
            target = command.user.get_user_id()
            trans_type = f"{command.action}_user"

        try:
            # Execute and explicitly check for False return value as failure
            result = command.execute()
            success = result if isinstance(result, bool) else True # Assume success if no explicit bool or exception

        except LibraryError as e:
            success = False
            error_details = str(e)
            # Don't re-raise, log it as failure
            print(f"Command failed: {e}") # Print feedback
        except Exception as e:
             success = False
             error_details = f"Unexpected error: {str(e)}"
             print(f"Command failed: {error_details}") # Print feedback

        # Log Transaction
        transaction = Transaction(actor, target, trans_type, success, error_details)
        self._history.append(transaction)
        # print(f"Logged Transaction: {transaction.get_details()}") # Optional debug print
        return success # Return final success status


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