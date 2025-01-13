class Error:
    def __init__(self, id: str, field: str, message: str):
        self.id = id
        self.field = field
        self.message = message
