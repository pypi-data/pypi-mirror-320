import unittest
from uk_police.exceptions import APIError, ValidationError, NotFoundError, RateLimitError, ServerError

class TestExceptions(unittest.TestCase):
    def test_api_error(self):
        error = APIError("An error occurred", 500)
        self.assertEqual(str(error), "500: An error occurred")

    def test_validation_error(self):
        error = ValidationError("Invalid input")
        self.assertEqual(str(error), "400: Invalid input")

    def test_not_found_error(self):
        error = NotFoundError()
        self.assertEqual(str(error), "404: Resource not found.")

    def test_rate_limit_error_with_retry(self):
        error = RateLimitError("Rate limit exceeded.", retry_after=10)
        self.assertEqual(str(error), "429: Rate limit exceeded. Retry after 10 seconds.")

    def test_server_error(self):
        error = ServerError("Internal server error")
        self.assertEqual(str(error), "500: Internal server error")

if __name__ == "__main__":
    unittest.main()
