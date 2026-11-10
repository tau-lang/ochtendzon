class OchtendzonError(Exception):
    """Error raised for non-recoverable errors."""

    def __init__(self, message):
        super().__init__(message)
