from datetime import datetime

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
