import unittest
from unittest.mock import patch
from uk_police.street_level import StreetLevelCrime

class TestStreetLevelCrime(unittest.TestCase):
    def setUp(self):
        self.client = StreetLevelCrime()

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_get_street_crimes_at_location(self, mock_get):
        mock_get.return_value = [
            {"category": "violent-crime", "location": {"latitude": "51.5074", "longitude": "-0.1278"}}
        ]
        lat, lng, date = 51.5074, -0.1278, "2024-01"
        result = self.client.get_street_crimes_at_location(lat, lng, date)
        mock_get.assert_called_once_with("crimes-street/all-crime", params={"lat": lat, "lng": lng, "date": date})
        self.assertEqual(result[0]["category"], "violent-crime")

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_get_street_crimes_in_area(self, mock_get):
        mock_get.return_value = [
            {"category": "burglary", "location": {"latitude": "51.5074", "longitude": "-0.1278"}}
        ]
        poly, date = "51.5074,-0.1278:51.5075,-0.1279", "2024-01"
        result = self.client.get_street_crimes_in_area(poly, date)
        mock_get.assert_called_once_with("crimes-street/all-crime", params={"poly": poly, "date": date})
        self.assertEqual(result[0]["category"], "burglary")

    def test_invalid_lat_lng(self):
        with self.assertRaises(ValueError):
            self.client.get_street_crimes_at_location(100.0, 200.0)

    def test_invalid_polygon(self):
        with self.assertRaises(ValueError):
            self.client.get_street_crimes_in_area("invalid-poly-string")

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_get_outcomes_at_location(self, mock_get):
        mock_get.return_value = [
            {"category": {"code": "local-resolution", "name": "Local resolution"}}
        ]
        location_id, date = "12345", "2024-01"
        result = self.client.get_outcomes_at_location(location_id, date)
        mock_get.assert_called_once_with("outcomes-at-location", params={"location_id": location_id, "date": date})
        self.assertEqual(result[0]["category"]["code"], "local-resolution")

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_get_outcomes_by_coordinates(self, mock_get):
        mock_get.return_value = [
            {"category": {"code": "charged", "name": "Suspect charged"}}
        ]
        lat, lng, date = 52.629729, -1.131592, "2024-01"
        result = self.client.get_outcomes_by_coordinates(lat, lng, date)
        mock_get.assert_called_once_with("outcomes-at-location", params={"lat": lat, "lng": lng, "date": date})
        self.assertEqual(result[0]["category"]["code"], "charged")

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_get_crimes_no_location(self, mock_get):
        mock_get.return_value = [
            {"category": "bicycle-theft", "location": None, "month": "2024-01"}
        ]
        category, force, date = "all-crime", "leicestershire", "2024-01"
        result = self.client.get_crimes_no_location(category, force, date)
        mock_get.assert_called_once_with(
            "crimes-no-location", params={"category": category, "force": force, "date": date}
        )
        self.assertEqual(result[0]["category"], "bicycle-theft")

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_get_crime_categories(self, mock_get):
        mock_get.return_value = [
            {"url": "all-crime", "name": "All crime and ASB"},
            {"url": "burglary", "name": "Burglary"}
        ]
        date = "2024-01"
        result = self.client.get_crime_categories(date)
        mock_get.assert_called_once_with("crime-categories", params={"date": date})
        self.assertEqual(result[0]["url"], "all-crime")

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_get_last_updated(self, mock_get):
        mock_get.return_value = {"date": "2024-10-01"}
        result = self.client.get_last_updated()
        mock_get.assert_called_once_with("crime-last-updated")
        self.assertEqual(result["date"], "2024-10-01")
    
    def test_invalid_poly_string(self):
        with self.assertRaises(ValueError):
            self.client.get_street_crimes_in_area(poly="invalid-poly")

    def test_invalid_crime_id(self):
        with self.assertRaises(ValueError):
            self.client.get_outcomes_for_crime(crime_id="short_id")

if __name__ == "__main__":
    unittest.main()
