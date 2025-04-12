class NotFoundException(RuntimeError):
    def __init_(self, message):
        super().__init__(message)