from Composite import *
from Book import *
from User import *

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
