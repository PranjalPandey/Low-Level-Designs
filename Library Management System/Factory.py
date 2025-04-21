
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
