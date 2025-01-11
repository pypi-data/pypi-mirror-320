from uk_police.client import uk_police
from uk_police.utils import validate_lat_lng, validate_polygon

class StopSearch:
    def __init__(self):
        self.client = uk_police()

    def stop_and_search_by_area(self, lat: float = None, lng: float = None, poly: str = None, date: str = None):
        """
        Retrieve stop and searches at street-level by a specific point or within a custom area.

        :param lat: (Optional) Latitude of the centre of the desired area.
        :param lng: (Optional) Longitude of the centre of the desired area.
        :param poly: (Optional) The lat/lng pairs which define the boundary of the custom area.
        :param date: (Optional) Date in YYYY-MM format. Defaults to the latest month.
        :return: List of stop and search records.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        if not ((lat and lng) or poly):
            raise ValueError("Either lat/lng or poly must be provided.")

        params = {}

        if lat and lng:
            validate_lat_lng(lat, lng)
            params.update({"lat": lat, "lng": lng})

        if poly:
            validate_polygon(poly)
            params["poly"] = poly

        if date:
            params["date"] = date

        return self.client._get_with_retry("stops-street", params=params)
    
    def stop_and_search_by_location(self, location_id: str, date: str = None):
        """
        Retrieve stop and searches at a specific location.

        :param location_id: The ID of the location to get stop and searches for.
        :param date: (Optional) Date in YYYY-MM format. Defaults to the latest month.
        :return: List of stop and search records.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        if not location_id:
            raise ValueError("location_id must be provided.")

        params = {"location_id": location_id}

        if date:
            params["date"] = date

        return self.client._get_with_retry("stops-at-location", params=params)
    
    def stop_and_search_no_location(self, force: str, date: str = None):
        """
        Retrieve stop and searches that could not be mapped to a location.

        :param force: The force that carried out the stop and searches.
        :param date: (Optional) Date in YYYY-MM format. Defaults to the latest month.
        :return: List of stop and search records with no location.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        if not force:
            raise ValueError("force must be provided.")

        params = {"force": force}

        if date:
            params["date"] = date

        return self.client._get_with_retry("stops-no-location", params=params)
    
    def stop_and_search_by_force(self, force: str, date: str = None):
        """
        Retrieve stop and searches reported by a particular force.

        :param force: The force ID of the force to get stop and searches for.
        :param date: (Optional) Date in YYYY-MM format. Defaults to the latest month.
        :return: List of stop and search records for the specified force.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        if not force:
            raise ValueError("force must be provided.")

        params = {"force": force}

        if date:
            params["date"] = date

        return self.client._get_with_retry("stops-force", params=params)
