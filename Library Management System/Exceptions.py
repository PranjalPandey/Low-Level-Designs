
# --- Custom Exceptions ---
class LibraryError(Exception):
    """Base class for library-specific errors."""
    pass

class BookNotFoundError(LibraryError):
    """Raised when a book is not found."""
    pass

class BookUnavailableError(LibraryError):
    """Raised when a book is not available for checkout or reservation."""
    pass

class AlreadyCheckedOutError(LibraryError):
    """Raised when trying to check out a book already checked out."""
    pass

class NotCheckedOutError(LibraryError):
    """Raised when trying to return a book not checked out by the user."""
    pass

class UserNotFoundError(LibraryError):
    """Raised when a user is not found."""
    pass

class InvalidOperationError(LibraryError):
    """Raised for operations that are not permitted (e.g., adding to a leaf)."""
    pass

class PermissionsError(LibraryError):
    """Raised when a user lacks permissions for an action."""
    pass

