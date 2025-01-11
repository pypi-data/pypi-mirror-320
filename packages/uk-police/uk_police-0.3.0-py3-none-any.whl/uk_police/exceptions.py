

class APIError(Exception):
    """Base exception for API errors."""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code

    def __str__(self):
        if self.status_code:
            return f"{self.status_code}: {super().__str__()}"
        return super().__str__()

class ValidationError(APIError):
    """Exception for invalid inputs."""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class NotFoundError(APIError):
    """Exception for 404 errors."""
    def __init__(self, message: str = "Resource not found."):
        super().__init__(message, status_code=404)

class RateLimitError(APIError):
    """Exception for rate limiting (429 errors)."""
    def __init__(self, message: str = "Rate limit exceeded.", retry_after: int = None):
        super().__init__(message, status_code=429)
        self.retry_after = retry_after

    def __str__(self):
        base_message = super().__str__()
        if self.retry_after:
            return f"{base_message} Retry after {self.retry_after} seconds."
        return base_message

class ServerError(APIError):
    """Exception for server-side errors (5xx)."""
    def __init__(self, message: str = "Server error."):
        super().__init__(message, status_code=500)