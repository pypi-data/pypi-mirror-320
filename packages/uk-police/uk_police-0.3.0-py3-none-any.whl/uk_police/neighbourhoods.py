from uk_police.client import uk_police
from uk_police.utils import validate_lat_lng

class Neighbourhoods:
    def __init__(self):
        self.client = uk_police()

    def list_neighbourhoods(self, force_id: str):
        """
        Retrieve a list of neighbourhoods for a specific police force.

        :param force_id: The unique identifier for the police force.
        :return: List of dictionaries containing neighbourhood IDs and names.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        if not force_id:
            raise ValueError("force_id must be provided.")

        return self.client._get_with_retry(f"{force_id}/neighbourhoods")
    
    def get_neighbourhood_details(self, force_id: str, neighbourhood_id: str):
        """
        Retrieve details about a specific neighbourhood within a police force.

        :param force_id: The unique identifier for the police force.
        :param neighbourhood_id: The unique identifier for the neighbourhood.
        :return: Dictionary containing details about the neighbourhood.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        if not force_id or not neighbourhood_id:
            raise ValueError("Both force_id and neighbourhood_id must be provided.")

        return self.client._get_with_retry(f"{force_id}/{neighbourhood_id}")
    
    def get_neighbourhood_boundary(self, force_id: str, neighbourhood_id: str):
        """
        Retrieve the boundary of a specific neighbourhood within a police force.

        :param force_id: The unique identifier for the police force.
        :param neighbourhood_id: The unique identifier for the neighbourhood.
        :return: List of dictionaries containing latitude and longitude pairs.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        if not force_id or not neighbourhood_id:
            raise ValueError("Both force_id and neighbourhood_id must be provided.")

        return self.client._get_with_retry(f"{force_id}/{neighbourhood_id}/boundary")
    
    def get_neighbourhood_team(self, force_id: str, neighbourhood_id: str):
        """
        Retrieve the team members for a specific neighbourhood within a police force.

        :param force_id: The unique identifier for the police force.
        :param neighbourhood_id: The unique identifier for the neighbourhood.
        :return: List of dictionaries containing team members' details.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        if not force_id or not neighbourhood_id:
            raise ValueError("Both force_id and neighbourhood_id must be provided.")

        return self.client._get_with_retry(f"{force_id}/{neighbourhood_id}/people")
    
    def get_neighbourhood_events(self, force_id: str, neighbourhood_id: str):
        """
        Retrieve events for a specific neighbourhood within a police force.

        :param force_id: The unique identifier for the police force.
        :param neighbourhood_id: The unique identifier for the neighbourhood.
        :return: List of dictionaries containing details about neighbourhood events.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        if not force_id or not neighbourhood_id:
            raise ValueError("Both force_id and neighbourhood_id must be provided.")

        return self.client._get_with_retry(f"{force_id}/{neighbourhood_id}/events")
    
    def get_neighbourhood_priorities(self, force_id: str, neighbourhood_id: str):
        """
        Retrieve priorities for a specific neighbourhood within a police force.

        :param force_id: The unique identifier for the police force.
        :param neighbourhood_id: The unique identifier for the neighbourhood.
        :return: List of dictionaries containing details about neighbourhood priorities.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        if not force_id or not neighbourhood_id:
            raise ValueError("Both force_id and neighbourhood_id must be provided.")

        return self.client._get_with_retry(f"{force_id}/{neighbourhood_id}/priorities")
    
    def locate_neighbourhood(self, latitude: float, longitude: float):
        """
        Find the neighbourhood policing team responsible for a particular area.

        :param latitude: Latitude of the location.
        :param longitude: Longitude of the location.
        :return: Dictionary containing the force and neighbourhood identifiers.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        validate_lat_lng(latitude, longitude)

        query = f"{latitude},{longitude}"
        return self.client._get_with_retry("locate-neighbourhood", params={"q": query})