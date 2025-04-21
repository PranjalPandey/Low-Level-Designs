from Exceptions import *
import abc
# --- Composite Pattern ---
class LibraryItem(abc.ABC):
    @abc.abstractmethod
    def display_info(self, indent=""):
        pass

    def add(self, item):
        raise InvalidOperationError("Cannot add items to this element.")

    def remove(self, item):
         raise InvalidOperationError("Cannot remove items from this element.")

    def get_books(self):
        return [] # Default for non-book items or empty collections
