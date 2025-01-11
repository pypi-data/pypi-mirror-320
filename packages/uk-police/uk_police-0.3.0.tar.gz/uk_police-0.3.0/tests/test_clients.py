import unittest
from unittest.mock import patch
from uk_police.client import uk_police
from uk_police.exceptions import *
import requests

class TestPyoliceClient(unittest.TestCase):
    def setUp(self):
        self.client = uk_police()

    @patch("requests.Session.get")
    def test_get_successful_response(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"key": "value"}

        endpoint = "test-endpoint"
        result = self.client._get(endpoint)

        # Assertions
        self.assertEqual(result, {"key": "value"})
        mock_get.assert_called_once_with(
            f"{self.client.BASE_URL}/{endpoint}", params=None, timeout=10
        )

    @patch("requests.Session.get")
    def test_get_with_params(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"key": "value"}

        endpoint = "test-endpoint"
        params = {"param1": "value1", "param2": "value2"}
        result = self.client._get(endpoint, params=params)

        self.assertEqual(result, {"key": "value"})
        mock_get.assert_called_once_with(
            f"{self.client.BASE_URL}/{endpoint}", params=params, timeout=10
        )

    @patch("requests.Session.get")
    def test_get_raises_api_error_on_failure(self, mock_get):
        from requests.exceptions import RequestException
        mock_get.side_effect = RequestException("Request failed")
        endpoint = "test-endpoint"
        with self.assertRaises(APIError):
            self.client._get(endpoint)

    @patch("requests.Session.get")
    def test_get_raises_api_error_on_non_200_status(self, mock_get):
        from requests.exceptions import RequestException
        mock_get.return_value.status_code = 404
        mock_get.return_value.raise_for_status.side_effect = RequestException("Not Found")
        endpoint = "test-endpoint"
        with self.assertRaises(APIError):
            self.client._get(endpoint)
    
    @patch("requests.Session.get")
    def test_rate_limit_retry(self, mock_get):
        # Mock rate limit and success responses
        mock_response_429 = unittest.mock.Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {"Retry-After": "2"}
        mock_response_429.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response_429)

        mock_response_200 = unittest.mock.Mock()
        mock_response_200.status_code = 200
        mock_response_200.raise_for_status.return_value = None
        mock_response_200.json.return_value = {"key": "value"}

        mock_get.side_effect = [mock_response_429, mock_response_200]  # First call fails, second call succeeds

        # Call the method and verify retries
        endpoint = "some-endpoint"
        result = self.client._get_with_retry(endpoint)

        self.assertEqual(result, {"key": "value"})
        self.assertEqual(mock_get.call_count, 2)

    @patch("requests.Session.get")
    def test_get_with_retry_all_fail(self, mock_get):
        """Test when all retry attempts fail due to 429 errors."""
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 429
        mock_response.headers = {}
        mock_response.raise_for_status.side_effect = RateLimitError("Rate limit exceeded.")
        mock_get.side_effect = [mock_response, mock_response, mock_response]  # All retries fail

        endpoint = "test-endpoint"
        with self.assertRaises(RateLimitError):
            self.client._get_with_retry(endpoint)
        self.assertEqual(mock_get.call_count, 3)

    @patch("requests.Session.get")
    def test_get_with_retry_missing_retry_after(self, mock_get):
        """Test when Retry-After header is missing, defaulting to 1-second wait."""
        mock_response_429 = unittest.mock.Mock()
        mock_response_429.status_code = 429
        mock_response_429.headers = {}
        mock_response_429.raise_for_status.side_effect = RateLimitError("Rate limit exceeded.")

        mock_response_200 = unittest.mock.Mock()
        mock_response_200.status_code = 200
        mock_response_200.raise_for_status.return_value = None
        mock_response_200.json.return_value = {"key": "value"}

        mock_get.side_effect = [mock_response_429, mock_response_200]

        endpoint = "test-endpoint"
        result = self.client._get_with_retry(endpoint)
        self.assertEqual(result, {"key": "value"})
        self.assertEqual(mock_get.call_count, 2)

    @patch("requests.Session.get")
    def test_timeout_handling(self, mock_get):
        """Simulate a timeout and ensure APIError is raised."""
        mock_get.side_effect = requests.exceptions.Timeout
        endpoint = "test-endpoint"
        with self.assertRaises(APIError):
            self.client._get(endpoint)


if __name__ == "__main__":
    unittest.main()
