import abc
from User import *
from Librarian import *

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

