import unittest
from unittest.mock import patch
from uk_police.forces import Forces

class TestForces(unittest.TestCase):
    def setUp(self):
        self.client = Forces()

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_list_forces(self, mock_get):
        mock_get.return_value = [
            {"id": "leicestershire", "name": "Leicestershire Police"},
            {"id": "metropolitan", "name": "Metropolitan Police Service"}
        ]
        result = self.client.list_forces()
        mock_get.assert_called_once_with("forces")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "leicestershire")
        self.assertEqual(result[1]["name"], "Metropolitan Police Service")

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_get_force_details(self, mock_get):
        mock_get.return_value = {
            "id": "leicestershire",
            "name": "Leicestershire Police",
            "description": "Serving Leicestershire and Rutland."
        }
        force_id = "leicestershire"
        result = self.client.get_force_details(force_id)
        mock_get.assert_called_once_with(f"forces/{force_id}")
        self.assertEqual(result["id"], "leicestershire")
        self.assertEqual(result["description"], "Serving Leicestershire and Rutland.")

    def test_get_force_details_invalid_id(self):
        with self.assertRaises(ValueError):
            self.client.get_force_details("")

    @patch("uk_police.client.uk_police._get_with_retry")
    def test_get_senior_officers(self, mock_get):
        mock_get.return_value = [
            {"name": "Chief Constable Simon Cole", "rank": "Chief Constable"},
            {"name": "Deputy Chief Constable Rob Nixon", "rank": "Deputy Chief Constable"}
        ]
        force_id = "leicestershire"
        result = self.client.get_senior_officers(force_id)
        mock_get.assert_called_once_with(f"forces/{force_id}/people")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["rank"], "Chief Constable")

    def test_get_senior_officers_invalid_id(self):
        with self.assertRaises(ValueError):
            self.client.get_senior_officers("")

if __name__ == "__main__":
    unittest.main()