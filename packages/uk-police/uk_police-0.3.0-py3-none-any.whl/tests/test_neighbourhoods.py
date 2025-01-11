import unittest
from unittest.mock import patch
from uk_police.neighbourhoods import Neighbourhoods

class TestNeighbourhoods(unittest.TestCase):
    def setUp(self):
        self.client = Neighbourhoods()

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_list_neighbourhoods(self, mock_get):
        mock_get.return_value = [
            {"id": "N01", "name": "Central"},
            {"id": "N02", "name": "East"}
        ]
        force_id = "leicestershire"
        result = self.client.list_neighbourhoods(force_id)
        mock_get.assert_called_once_with(f"{force_id}/neighbourhoods")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "N01")

    def test_list_neighbourhoods_invalid_force(self):
        with self.assertRaises(ValueError):
            self.client.list_neighbourhoods("")

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_get_neighbourhood_details(self, mock_get):
        mock_get.return_value = {
            "id": "N01",
            "name": "Central",
            "description": "The central neighbourhood in the force."
        }
        force_id = "leicestershire"
        neighbourhood_id = "N01"
        result = self.client.get_neighbourhood_details(force_id, neighbourhood_id)
        mock_get.assert_called_once_with(f"{force_id}/{neighbourhood_id}")
        self.assertEqual(result["id"], "N01")

    def test_get_neighbourhood_details_invalid_input(self):
        with self.assertRaises(ValueError):
            self.client.get_neighbourhood_details("", "N01")

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_get_neighbourhood_boundary(self, mock_get):
        mock_get.return_value = [
            {"latitude": 52.634770, "longitude": -1.129407},
            {"latitude": 52.636850, "longitude": -1.135171}
        ]
        force_id = "leicestershire"
        neighbourhood_id = "N01"
        result = self.client.get_neighbourhood_boundary(force_id, neighbourhood_id)
        mock_get.assert_called_once_with(f"{force_id}/{neighbourhood_id}/boundary")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["latitude"], 52.634770)

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_get_neighbourhood_team(self, mock_get):
        mock_get.return_value = [
            {"name": "PC John Doe", "rank": "Police Constable"},
            {"name": "Sgt Jane Smith", "rank": "Sergeant"}
        ]
        force_id = "leicestershire"
        neighbourhood_id = "N01"
        result = self.client.get_neighbourhood_team(force_id, neighbourhood_id)
        mock_get.assert_called_once_with(f"{force_id}/{neighbourhood_id}/people")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["rank"], "Police Constable")

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_get_neighbourhood_events(self, mock_get):
        mock_get.return_value = [
            {"title": "Community Meeting", "description": "Discuss local issues."},
            {"title": "Crime Awareness", "description": "Learn about crime prevention."}
        ]
        force_id = "leicestershire"
        neighbourhood_id = "N01"
        result = self.client.get_neighbourhood_events(force_id, neighbourhood_id)
        mock_get.assert_called_once_with(f"{force_id}/{neighbourhood_id}/events")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["title"], "Community Meeting")

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_get_neighbourhood_priorities(self, mock_get):
        mock_get.return_value = [
            {"issue": "Reduce anti-social behavior", "action": "Increase patrols in the area."}
        ]
        force_id = "leicestershire"
        neighbourhood_id = "N01"
        result = self.client.get_neighbourhood_priorities(force_id, neighbourhood_id)
        mock_get.assert_called_once_with(f"{force_id}/{neighbourhood_id}/priorities")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["issue"], "Reduce anti-social behavior")

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_locate_neighbourhood(self, mock_get):
        mock_get.return_value = {"force": "leicestershire", "neighbourhood": "N01"}
        latitude, longitude = 52.634770, -1.129407
        result = self.client.locate_neighbourhood(latitude, longitude)
        mock_get.assert_called_once_with("locate-neighbourhood", params={"q": f"{latitude},{longitude}"})
        self.assertEqual(result["force"], "leicestershire")
        self.assertEqual(result["neighbourhood"], "N01")

    def test_locate_neighbourhood_invalid_lat_lng(self):
        with self.assertRaises(ValueError):
            self.client.locate_neighbourhood(100.0, 200.0)

if __name__ == "__main__":
    unittest.main()