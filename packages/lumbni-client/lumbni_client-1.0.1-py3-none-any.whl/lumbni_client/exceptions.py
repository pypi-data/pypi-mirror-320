class LumbniApiError(Exception):
    """Exception raised for errors in the Lumbni API."""
    
    def __init__(self, message: str, status_code: int = None, details: str = None):
        super().__init__(message)
        self.status_code = status_code
        self.details = details

    def __str__(self):
        error_message = f"{self.args[0]}"
        if self.status_code:
            error_message += f" (Status Code: {self.status_code})"
        if self.details:
            error_message += f" - Details: {self.details}"
        return error_message
