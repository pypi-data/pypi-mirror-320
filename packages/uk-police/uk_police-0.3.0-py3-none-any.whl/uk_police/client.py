import requests, time
from .exceptions import *

class uk_police:
    BASE_URL = "https://data.police.uk/api"

    def __init__(self):
        self.client = requests.Session()
    
    def close(self):
        """Closes the active client"""
        self.client.close()

    def _get(self, endpoint: str, params: dict = None):
        """Send a GET request to the UK Police API."""
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.client.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise APIError("Request timed out.")
        except requests.exceptions.HTTPError as e:
            response = getattr(e, "response", None)  # Get the response object from the exception
            if response:
                status_code = response.status_code
                if status_code == 400:
                    raise ValidationError(f"Bad request: {response.text}")
                elif status_code == 404:
                    raise NotFoundError(f"Not found: {url}")
                elif status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 1))
                    raise RateLimitError(
                        f"Rate limit exceeded. Retry after {retry_after} seconds.",
                        retry_after=retry_after
                    )
                elif 500 <= status_code < 600:
                    raise ServerError(f"Server error ({status_code}): {response.text}")
            raise APIError(f"HTTP error occurred: {e}")
        except requests.exceptions.RequestException as e:
            raise APIError(f"An error occurred: {e}")
        
    def _get_with_retry(self, endpoint: str, params: dict = None, max_retries: int = 3):
        """Send a GET request with retry support for rate limits."""
        for attempt in range(max_retries):
            try:
                return self._get(endpoint, params)
            except RateLimitError as e:
                if attempt < max_retries - 1:
                    wait_time = e.retry_after or 1
                    print(f"Rate limit exceeded. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    raise
