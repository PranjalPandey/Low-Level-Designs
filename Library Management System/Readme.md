# Library Management System: A Low-Level Design Example in Python

## Overview

This project implements a basic Library Management System in Python. Its primary goal is not to be a production-ready application, but rather to serve as an educational example demonstrating fundamental Object-Oriented Programming (OOP) principles and common Low-Level Design (LLD) patterns. Learners can explore this code to understand how different design patterns can be applied to structure code, improve maintainability, and enhance flexibility in a practical context.

The system simulates core library operations like managing books and users, handling checkouts, returns, reservations, fines, and generating reports.

## Features

* **Book Management:** Add, remove, and update the status of books (available, checked out, reserved, lost, damaged, archived).
* **Hierarchical Catalog:** Organize books into collections (e.g., genres) using a composite structure.
* **User Management:** Register and remove users.
* **Librarian Role:** Distinct staff role with specific permissions (managing books and users).
* **Core Operations:** Checkout, return, and reserve books.
* **Waitlist:** Automatic handling of waitlists for checked-out books.
* **Fine Calculation:** Basic calculation and tracking of fines for overdue books.
* **Notifications:** Simple notification system (using the Observer pattern) for events like overdue books, reservations becoming available, etc.
* **Transaction Logging:** Records actions performed within the system.
* **Reporting:** Generate basic summaries of library status.
* **Search:** Find books by title, author, or ISBN.
* **Robust Error Handling:** Uses custom exceptions for specific error conditions.

## Core Concepts & Design Patterns Illustrated

This system is designed around several key LLD principles and design patterns:

### 1. Core Classes & Responsibilities

* **`Library`**: The central orchestrator. Acts as a Singleton to ensure only one library instance exists. Holds the main book catalog, user lists, and the command invoker. Manages library-wide configurations (e.g., fine rates).
* **`User`**: Represents a library member who can borrow, return, and reserve books, incur fines, and receive notifications. Acts as an `Observer`.
* **`Librarian`**: Represents library staff. Has permissions to manage the catalog (add/remove items), manage users, and update book statuses. *Note: This class is distinct from `User` and does not inherit from it, reflecting different roles.*
* **`LibraryItem` (Abstract)**: The base class for items in the library catalog, defining a common interface (used by the Composite pattern).
* **`Book`**: Represents a single book (a 'Leaf' node in the Composite pattern). It's also a `Subject` in the Observer pattern, notifying users about status changes, reservations, etc. Holds details like title, author, ISBN, status, borrower, due date, and waitlist.
* **`BookCollection`**: Represents a collection of `LibraryItem`s (a 'Composite' node). Allows grouping books or other collections hierarchically.
* **`Command` (Abstract & Concrete)**: Encapsulates actions (like checkout, return, add item) as objects.
* **`CommandInvoker`**: Executes `Command` objects and logs `Transaction`s.
* **`Transaction`**: A simple data object recording details of executed commands (actor, target, success, timestamp).
* **Custom Exceptions**: Specific error classes (`BookUnavailableError`, `UserNotFoundError`, etc.) derived from a base `LibraryError` for better error handling.

### 2. Design Patterns Applied

* **Singleton Pattern (`Library` class):**
    * **Purpose:** Ensures that only one instance of the `Library` class exists throughout the application. This is useful for managing a single, shared resource (the library itself).
    * **Implementation:** Uses a private class variable `_instance` and a static method `get_instance()` to control instantiation. The constructor prevents direct creation after the first instance.

* **Factory Pattern (`PersonFactory` class):**
    * **Purpose:** Decouples the object creation logic from the client code. The client requests an object of a certain type ('user' or 'librarian') without needing to know the specific class name or instantiation details.
    * **Implementation:** The `create_person` static method takes the type and parameters, returning an instance of the appropriate class (`User` or `Librarian`).

* **Observer Pattern (`Subject`, `Observer`, `Book`, `User` classes):**
    * **Purpose:** Defines a one-to-many dependency between objects. When one object (`Subject`, e.g., `Book`) changes state, all its dependents (`Observer`s, e.g., `User`s on the waitlist or the current borrower) are notified automatically.
    * **Implementation:** `Subject` provides `attach`, `detach`, `notify` methods. `Observer` provides an `update` method. `Book` (as Subject) calls `notify` when its status changes (checkout, return, reserved, etc.). `User` (as Observer) implements `update` to react to these notifications. Users are attached/detached dynamically based on borrowing or joining/leaving a waitlist.

* **Command Pattern (`Command` hierarchy, `CommandInvoker`):**
    * **Purpose:** Encapsulates a request (action) as an object. This allows parameterizing clients with different requests, queuing requests, logging requests, and potentially supporting undoable operations (though undo is not implemented here). It decouples the object initiating an action (e.g., a UI element in a larger app) from the object performing the action (e.g., `User`, `Librarian`).
    * **Implementation:** An abstract `Command` class defines an `execute` method. Concrete commands (`CheckoutBookCommand`, `AddItemCommand`, etc.) implement `execute` by calling the appropriate methods on the receiver objects (`User` or `Librarian`). The `CommandInvoker` takes command objects and calls their `execute` method, centralizing action execution and enabling transaction logging.

* **Composite Pattern (`LibraryItem`, `Book`, `BookCollection` classes):**
    * **Purpose:** Allows composing objects into tree structures to represent part-whole hierarchies. It lets clients treat individual objects (`Book`) and compositions of objects (`BookCollection`) uniformly.
    * **Implementation:** The `LibraryItem` abstract class defines the common interface (e.g., `display_info`, `get_books`). `Book` is the 'Leaf' component. `BookCollection` is the 'Composite' component, holding a list of child `LibraryItem`s and delegating operations to them. The `Library`'s catalog is a `BookCollection`, enabling nested structures.

## Error Handling

Instead of just printing error messages, the system uses custom exception classes inheriting from `LibraryError`. When an operation cannot be completed (e.g., trying to check out an unavailable book, finding a non-existent user), a specific exception is `raised`. This allows the calling code (like the `CommandInvoker` or the main script) to `catch` these specific errors and handle them more gracefully (e.g., logging the failure, informing the user).

## Transaction Logging

The `CommandInvoker` logs every attempted command execution into a `Transaction` object. This object stores:
* Who performed the action (`actor_id`)
* What the action targeted (`target_id`)
* The type of action (`transaction_type`)
* Whether it succeeded or failed (`success`)
* Timestamp and a unique ID.

This provides a basic audit trail for library operations.

## How to Run

1.  Save the code as a Python file (e.g., `library_system.py`).
2.  Run the file from your terminal:
    ```bash
    python library_system.py
    ```
3.  Observe the output, which demonstrates the creation of users and books, various operations (checkout, return, reserve), error handling, notifications, and the final report and transaction history based on the example usage block at the end of the script.

## Areas for Further Learning / Extension

This example provides a foundation. Learners can extend it by:

* Adding a Graphical User Interface (GUI) using Tkinter, PyQt, or Kivy.
* Integrating a database (like SQLite, PostgreSQL) for persistent storage instead of keeping data in memory.
* Implementing more advanced features (e.g., detailed loan history per user, book recommendation logic, user roles/permissions).
* Writing unit tests (using `unittest` or `pytest`) to verify the functionality of each component.
* Exposing the system via a web framework (like Flask or Django) as an API.
* Implementing an Undo/Redo mechanism using the Command pattern history.

## Conclusion

This project offers a practical demonstration of how low-level design principles and patterns can be used to build a modular, understandable, and extensible software system. By studying the interaction between the classes and the application of patterns like Singleton, Factory, Observer, Command, and Composite, learners can gain valuable insights into effective object-oriented design.