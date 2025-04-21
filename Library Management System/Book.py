# --- Book Class ---
class Book(LibraryItem, Subject):
    VALID_STATUSES = ["available", "checked out", "reserved", "lost", "damaged", "archived"]

    def __init__(self, title, author, isbn):
        LibraryItem.__init__(self)
        Subject.__init__(self)
        self.title = title
        self.author = author
        self.isbn = isbn
        self._status = "available"
        self.due_date = None
        self.borrower = None # User object who borrowed/reserved
        self.waitlist = [] # List of User objects waiting

    def get_title(self): return self.title
    def get_author(self): return self.author
    def get_isbn(self): return self.isbn
    def get_status(self): return self._status

    def _can_checkout(self, user):
        """Check if the book can be checked out by the given user."""
        if self._status == "available":
            return True
        if self._status == "reserved" and self.borrower == user:
            return True
        return False

    def _can_reserve(self, user):
        """Check if the book can be reserved by the given user."""
        # Can reserve if checked out AND user isn't already borrowing or on waitlist
        return self._status == "checked out" and \
               self.borrower != user and \
               user not in self.waitlist

    def add_to_waitlist(self, user: Observer):
        """Adds a user to the waitlist if they aren't already on it."""
        if user not in self.waitlist and isinstance(user, Observer):
            self.waitlist.append(user)
            self.attach(user) # Attach user to observe status changes
            self.notify(f"User {user.get_name()} added to waitlist for '{self.title}'.")
            print(f"{user.get_name()} added to waitlist for '{self.title}'. Position: {len(self.waitlist)}")
            return True
        return False

    def _process_waitlist(self):
        """Processes the waitlist when a book becomes available."""
        if self.waitlist:
            next_user = self.waitlist.pop(0)
            self._set_status("reserved", user=next_user) # Set status internally
            print(f"Book '{self.title}' is now reserved for {next_user.get_name()}.")
            # Observer notification happens within _set_status
        else:
            self._set_status("available") # Becomes available if waitlist is empty

    def _set_status(self, status: str, user=None, due_date=None):
        """Internal method to set status and handle notifications/observers."""
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {status}")

        old_status = self._status
        self._status = status
        message = f"Book '{self.title}' status changed from {old_status} to {status}"

        # Clear previous state if necessary
        if status != "checked out" and status != "reserved":
            self.borrower = None
            self.due_date = None

        if status == "checked out":
            self.borrower = user
            self.due_date = due_date
            if user and isinstance(user, Observer):
                self.attach(user) # Ensure borrower observes
            message += f" by {user.get_name() if user else 'N/A'}"
            if due_date: message += f". Due: {due_date}"
        elif status == "reserved":
            self.borrower = user # User for whom it is reserved
            message += f" for {user.get_name() if user else 'N/A'}"
        elif status == "available":
             # Detach previous borrower *only if* they are not on waitlist anymore
            if old_status in ["checked out", "reserved"] and self.borrower and \
               isinstance(self.borrower, Observer) and self.borrower not in self.waitlist:
                 self.detach(self.borrower)
            self.borrower = None
            self.due_date = None
        elif status in ["lost", "damaged", "archived"]:
             # Detach borrower/reserver if any
             if old_status in ["checked out", "reserved"] and self.borrower and \
                isinstance(self.borrower, Observer) and self.borrower not in self.waitlist:
                 self.detach(self.borrower)
             # Clear waitlist? Maybe notify waiting users it's unavailable indefinitely?
             # For now, just clear borrower/due date
             self.borrower = None
             self.due_date = None


        self.notify(message + ".") # Notify all current observers

    # --- Public methods to change status (used by Commands) ---
    def checkout(self, user: Observer, due_date):
        if not self._can_checkout(user):
             raise BookUnavailableError(f"'{self.title}' cannot be checked out by {user.get_name()}. Status: {self._status}")
        self._set_status("checked out", user=user, due_date=due_date)

    def return_book(self):
        if self._status != "checked out":
             raise NotCheckedOutError(f"'{self.title}' is not currently checked out.")
        # Process waitlist *first* before setting generally available
        self._process_waitlist() # This internally calls _set_status to 'reserved' or 'available'

    def update_status(self, new_status: str):
        """For Librarian use: Set status to lost, damaged, archived, or available."""
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}")
        if self._status == "checked out" and new_status in ["lost", "damaged"]:
            # Special handling: Book lost/damaged while checked out
            # Notify user, potentially add replacement fine (implementation specific)
            print(f"WARNING: Book '{self.title}' marked as {new_status} while checked out by {self.borrower.get_name()}.")
            # Optional: self.borrower.add_fine(REPLACEMENT_COST)
        self._set_status(new_status, user=None) # Set status without specific user context


    def display_info(self, indent=""):
        borrower_info = f", Borrower: {self.borrower.get_name()}" if self.borrower else ""
        due_info = f", Due: {self.due_date}" if self.due_date else ""
        waitlist_info = f", Waitlist: {len(self.waitlist)}" if self.waitlist else ""
        print(f"{indent}- Title: {self.title}, Author: {self.author}, ISBN: {self.isbn}, Status: {self._status}{borrower_info}{due_info}{waitlist_info}")

    def get_books(self):
        return [self]


# --- Book Collection (Composite - Unchanged) ---
class BookCollection(LibraryItem):
    def __init__(self, name):
        self._children = []
        self.name = name

    def add(self, item: LibraryItem):
        self._children.append(item)

    def remove(self, item: LibraryItem):
        if item in self._children:
            self._children.remove(item)
        else:
            # Try removing recursively? For now, only top-level removal in collection.
            raise BookNotFoundError(f"Item '{getattr(item, 'name', getattr(item, 'title', 'Unknown'))}' not found directly in collection '{self.name}'.")


    def display_info(self, indent=""):
        print(f"{indent}+ Collection: {self.name}")
        for child in self._children:
            child.display_info(indent + "  ")

    def get_books(self):
        all_books = []
        for child in self._children:
            all_books.extend(child.get_books())
        return all_books