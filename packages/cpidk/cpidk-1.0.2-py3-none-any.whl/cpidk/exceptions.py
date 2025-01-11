from typing import Optional


class ServerError(Exception):
    def __init__(self, message: Optional[str]):
        self.message = message
        super().__init__(message)

class UnknownError(Exception):
    def __init__(self, e: Exception):
        super().__init__(e)

