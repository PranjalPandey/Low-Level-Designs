
# --- Observer Pattern (Unchanged) ---
class Observer(abc.ABC):
    @abc.abstractmethod
    def update(self, subject, message):
        pass

class Subject(abc.ABC):
    def __init__(self):
        self._observers = []

    def attach(self, observer: Observer):
        if observer not in self._observers:
            self._observers.append(observer)

    def detach(self, observer: Observer):
        try:
            self._observers.remove(observer)
        except ValueError:
            pass

    def notify(self, message=None):
        # Create a copy for iteration in case observers detach themselves during update
        observers_copy = self._observers[:]
        for observer in observers_copy:
            observer.update(self, message)
