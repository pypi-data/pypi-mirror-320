import unittest
from unittest.mock import patch
from uk_police.stop_search import StopSearch

class TestStopSearch(unittest.TestCase):
    def setUp(self):
        self.client = StopSearch()

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_stop_and_search_by_area_with_coordinates(self, mock_get):
        mock_get.return_value = [
            {"category": "drugs", "outcome": "positive result", "location": {"latitude": 52.629729, "longitude": -1.131592}}
        ]
        lat, lng, date = 52.629729, -1.131592, "2024-01"
        result = self.client.stop_and_search_by_area(lat=lat, lng=lng, date=date)
        mock_get.assert_called_once_with("stops-street", params={"lat": lat, "lng": lng, "date": date})
        self.assertEqual(result[0]["category"], "drugs")

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_stop_and_search_by_area_with_polygon(self, mock_get):
        mock_get.return_value = [
            {"category": "weapons", "outcome": "arrest", "location": {"latitude": 52.634770, "longitude": -1.129407}}
        ]
        poly, date = "52.634770,-1.129407:52.636850,-1.135171", "2024-01"
        result = self.client.stop_and_search_by_area(poly=poly, date=date)
        mock_get.assert_called_once_with("stops-street", params={"poly": poly, "date": date})
        self.assertEqual(result[0]["category"], "weapons")

    def test_stop_and_search_by_area_invalid_inputs(self):
        with self.assertRaises(ValueError):
            self.client.stop_and_search_by_area()

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_stop_and_search_by_location(self, mock_get):
        mock_get.return_value = [
            {"category": "alcohol", "outcome": "no further action", "location": {"name": "Market Street"}}
        ]
        location_id, date = "12345", "2024-01"
        result = self.client.stop_and_search_by_location(location_id, date)
        mock_get.assert_called_once_with("stops-at-location", params={"location_id": location_id, "date": date})
        self.assertEqual(result[0]["category"], "alcohol")

    def test_stop_and_search_by_location_invalid_id(self):
        with self.assertRaises(ValueError):
            self.client.stop_and_search_by_location("")

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_stop_and_search_no_location(self, mock_get):
        mock_get.return_value = [
            {"category": "vehicle", "outcome": "no action", "location": None}
        ]
        force, date = "leicestershire", "2024-01"
        result = self.client.stop_and_search_no_location(force, date)
        mock_get.assert_called_once_with("stops-no-location", params={"force": force, "date": date})
        self.assertEqual(result[0]["category"], "vehicle")

    def test_stop_and_search_no_location_invalid_force(self):
        with self.assertRaises(ValueError):
            self.client.stop_and_search_no_location("")

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_stop_and_search_by_force(self, mock_get):
        mock_get.return_value = [
            {"category": "drugs", "outcome": "arrest", "location": {"name": "City Centre"}}
        ]
        force, date = "metropolitan", "2024-01"
        result = self.client.stop_and_search_by_force(force, date)
        mock_get.assert_called_once_with("stops-force", params={"force": force, "date": date})
        self.assertEqual(result[0]["category"], "drugs")

    def test_stop_and_search_by_force_invalid_force(self):
        with self.assertRaises(ValueError):
            self.client.stop_and_search_by_force("")

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_stop_and_search_by_area_valid(self, mock_get):
        mock_get.return_value = [{"type": "stop_and_search"}]
        result = self.client.stop_and_search_by_area(lat=51.5074, lng=-0.1278)
        self.assertEqual(result, [{"type": "stop_and_search"}])
    
    def test_stop_and_search_by_area_invalid(self):
        with self.assertRaises(ValueError):
            self.client.stop_and_search_by_area()  # Missing lat/lng or poly

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_stop_and_search_by_location_valid(self, mock_get):
        mock_get.return_value = [{"type": "stop_and_search"}]
        result = self.client.stop_and_search_by_location(location_id="123")
        self.assertEqual(result, [{"type": "stop_and_search"}])

    def test_stop_and_search_by_location_invalid(self):
        with self.assertRaises(ValueError):
            self.client.stop_and_search_by_location(location_id=None)

    def test_stop_and_search_missing_lat_lng_poly(self):
        with self.assertRaises(ValueError):
            self.client.stop_and_search_by_area()

    def test_stop_and_search_invalid_lat_lng(self):
        with self.assertRaises(ValueError):
            self.client.stop_and_search_by_area(lat=200, lng=200)  # Invalid coordinates

    def test_stop_and_search_invalid_poly(self):
        with self.assertRaises(ValueError):
            self.client.stop_and_search_by_area(poly="invalid-poly")

    def test_stop_and_search_missing_force(self):
        with self.assertRaises(ValueError):
            self.client.stop_and_search_no_location(force="")
    

if __name__ == "__main__":
    unittest.main()