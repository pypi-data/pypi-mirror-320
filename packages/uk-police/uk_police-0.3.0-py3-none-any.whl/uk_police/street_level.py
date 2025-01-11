from uk_police.client import uk_police
from uk_police.utils import validate_lat_lng, validate_polygon

'''
Handles street level crime related info
'''

class StreetLevelCrime:
    def __init__(self):
        self.client = uk_police()

    def get_street_crimes_at_location(self, lat: float, lng: float, date: str = None):
        """
        Retrieve crimes at a specific location.
        
        :param lat: Latitude of the location.
        :param lng: Longitude of the location.
        :param date: (Optional) Date in YYYY-MM format. Defaults to the latest month.
        :return: List of crimes at the given location.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        # validate given is correct
        validate_lat_lng(lat, lng)

        params = {"lat": lat, "lng": lng}

        # As date is optional
        if date:
            params["date"] = date


        return self.client._get_with_retry("crimes-street/all-crime", params=params)

    def get_street_crimes_in_area(self, poly: str, date: str = None):
        """
        Retrieve crimes in a specific custom area.
        
        :param poly: The lat/lng pairs defining the area boundary (format: [lat,lng]:[lat,lng]).
        :param date: (Optional) Date in YYYY-MM format. Defaults to the latest month.
        :return: List of crimes in the specified area.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        # validate its correct
        validate_polygon(poly)

        params = {"poly": poly}
        if date:
            params["date"] = date
            
        return self.client._get_with_retry("crimes-street/all-crime", params=params)
    
    def get_outcomes_at_location(self, location_id: str, date: str = None):
        """
        Retrieve street-level outcomes for a specific location.

        :param location_id: ID of the location.
        :param date: (Optional) Date in YYYY-MM format. Defaults to the latest month.
        :return: List of outcomes at the specified location.
        :raises: APIError for request failures.
        """
        if not location_id:
            raise ValueError("location_id must be provided.")

        params = {"location_id": location_id}
        if date:
            params["date"] = date

        return self.client._get_with_retry("outcomes-at-location", params=params)

    def get_outcomes_by_coordinates(self, lat: float, lng: float, date: str = None):
        """
        Retrieve street-level outcomes within a 1-mile radius of coordinates.

        :param lat: Latitude of the location.
        :param lng: Longitude of the location.
        :param date: (Optional) Date in YYYY-MM format. Defaults to the latest month.
        :return: List of outcomes near the given coordinates.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        validate_lat_lng(lat, lng)

        params = {"lat": lat, "lng": lng}
        if date:
            params["date"] = date

        return self.client._get_with_retry("outcomes-at-location", params=params)

    def get_outcomes_in_area(self, poly: str, date: str = None):
        """
        Retrieve street-level outcomes for a custom area.

        :param poly: The lat/lng pairs defining the area boundary (format: [lat,lng]:[lat,lng]).
        :param date: (Optional) Date in YYYY-MM format. Defaults to the latest month.
        :return: List of outcomes in the specified area.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        validate_polygon(poly)

        params = {"poly": poly}
        if date:
            params["date"] = date

        return self.client._get_with_retry("outcomes-at-location", params=params)
    
    def get_crimes_at_specific_location(self, location_id: str = None, lat: float = None, lng: float = None, date: str = None):
        """
        Retrieve crimes at a specific location, or by latitude/longitude.

        :param location_id: (Optional) ID of the specific location.
        :param lat: (Optional) Latitude of the location.
        :param lng: (Optional) Longitude of the location.
        :param date: (Optional) Date in YYYY-MM format. Defaults to the latest month.
        :return: List of crimes at the specified location.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        if not location_id and (lat is None or lng is None):
            raise ValueError("Either location_id or lat/lng must be provided.")

        params = {}
        if location_id:
            params["location_id"] = location_id
        elif lat is not None and lng is not None:
            validate_lat_lng(lat, lng)
            params["lat"] = lat
            params["lng"] = lng
        
        if date:
            params["date"] = date

        return self.client._get_with_retry("crimes-at-location", params=params)
    
    def get_crimes_no_location(self, category: str, force: str, date: str = None):
        """
        Retrieve a list of crimes that could not be mapped to a location.

        :param category: The category of the crimes (e.g., 'all-crime').
        :param force: Specific police force (e.g., 'leicestershire').
        :param date: (Optional) Date in YYYY-MM format. Defaults to the latest month.
        :return: List of crimes with no location.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        if not category or not force:
            raise ValueError("Both 'category' and 'force' parameters are required.")

        params = {
            "category": category,
            "force": force,
        }
        if date:
            params["date"] = date

        return self.client._get_with_retry("crimes-no-location", params=params)
    
    def get_crime_categories(self, date: str = None):
        """
        Retrieve a list of valid crime categories for a given data set date.

        :param date: (Optional) Date in YYYY-MM format. Defaults to the latest month.
        :return: List of valid crime categories.
        :raises: APIError for request failures.
        """
        params = {}
        if date:
            params["date"] = date

        return self.client._get_with_retry("crime-categories", params=params)
    
    def get_last_updated(self):
        """
        Retrieve the date when the crime data was last updated.

        :return: Dictionary containing the date in ISO format.
        :raises: APIError for request failures.
        """
        return self.client._get_with_retry("crime-last-updated")
    
    def get_outcomes_for_crime(self, crime_id: str):
        """
        Retrieve the outcomes (case history) for the specified crime.

        :param crime_id: The 64-character unique identifier of the crime.
        :return: Dictionary containing crime details and a list of outcomes.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        if not crime_id or len(crime_id) != 64:
            raise ValueError("A valid 64-character crime ID must be provided.")

        return self.client._get_with_retry(f"outcomes-for-crime/{crime_id}")