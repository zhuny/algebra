class WorkInProgressError(Exception):
    default_message = "This feature or section is still under development."

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message)


class Unreachable(Exception):
    default_message = "This code path should be unreachable."

    def __init__(self, message: str | None = None):
        super().__init__(message or self.default_message)
