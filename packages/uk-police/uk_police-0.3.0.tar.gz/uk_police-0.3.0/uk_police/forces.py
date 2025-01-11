from uk_police.client import uk_police

'''
Handles police forces related info
'''

class Forces:
    def __init__(self):
        self.client = uk_police()

    def list_forces(self):
        """
        Retrieve a list of all police forces available via the API except the British Transport Police.

        :return: List of dictionaries containing force IDs and names.
        :raises: APIError for request failures.
        """
        return self.client._get_with_retry("forces")
    
    def get_force_details(self, force_id: str):
        """
        Retrieve details about a specific police force by its unique identifier.

        :param force_id: The unique identifier for the police force.
        :return: Dictionary containing details about the police force.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        if not force_id:
            raise ValueError("force_id must be provided.")

        return self.client._get_with_retry(f"forces/{force_id}")
    
    def get_senior_officers(self, force_id: str):
        """
        Retrieve a list of senior officers for a specific police force.

        :param force_id: The unique identifier for the police force.
        :return: List of dictionaries containing details about senior officers.
        :raises: ValueError for invalid inputs, APIError for request failures.
        """
        if not force_id:
            raise ValueError("force_id must be provided.")

        return self.client._get_with_retry(f"forces/{force_id}/people")
    

if __name__ == "__main__":
    forces_client = Forces()

    # List all forces
    forces_list = forces_client.list_forces()
    for force in forces_list:
        print(f"{force['id']}: {force['name']}")

    # Get details for a specific force
    force_details = forces_client.get_force_details("leicestershire")
    print(force_details)

    # Get senior officers for a specific force
    senior_officers = forces_client.get_senior_officers("leicestershire")
    for officer in senior_officers:
        print(f"{officer['name']} ({officer['rank']}): {officer['bio']}")
