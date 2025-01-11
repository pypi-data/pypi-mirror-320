import unittest
from uk_police.utils import validate_lat_lng, validate_polygon

class TestUtils(unittest.TestCase):
    def test_validate_lat_lng_valid(self):
        self.assertIsNone(validate_lat_lng(51.5074, -0.1278))  # Valid

    def test_validate_lat_lng_invalid_lat(self):
        with self.assertRaises(ValueError):
            validate_lat_lng(100, -0.1278)  # Invalid latitude

    def test_validate_lat_lng_invalid_lng(self):
        with self.assertRaises(ValueError):
            validate_lat_lng(51.5074, -200)  # Invalid longitude

    def test_validate_polygon_valid(self):
        self.assertIsNone(validate_polygon("51.5,-0.1:51.5,-0.2"))  # Valid

    def test_validate_polygon_invalid_format(self):
        with self.assertRaises(ValueError):
            validate_polygon("51.5,-0.1,51.5,-0.2")  # Missing colon separator

    def test_validate_polygon_invalid_lat_lng(self):
        with self.assertRaises(ValueError):
            validate_polygon("51.5,-0.1:100,-200")  # Invalid lat/lng values


