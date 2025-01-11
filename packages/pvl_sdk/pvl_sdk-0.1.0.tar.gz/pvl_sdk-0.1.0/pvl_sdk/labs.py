# from .client import APIClient
# from .models import Lab


# class LabsAPI:
#     def __init__(self, client: APIClient):
#         self.client = client

#     def create_lab(self, lab_id: str, name: str, nodes: list):
#         lab = Lab(id=lab_id, name=name, nodes=nodes)
#         # data = {"id": lab_id, "name": name, "nodes": nodes}
#         return self.client.request("POST", "/labs", json=lab.dict())

#     def get_lab(self, lab_id: str):
#         return self.client.request("GET", f"/labs/{lab_id}")


from .client import APIClient
from .models import Lab


class LabsAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def authenticate(self, email: str, password: str) -> bool:
        """
        Authenticates the user by calling the /cml_users API and validating the credentials.
        """
        # Fetch all CML users from the backend
        response = self.client.request("GET", "/cml_users")
        
        # Access the 'users' key in the response
        users = response.get('users', [])  # Default to an empty list if 'users' key is missing

        # Check if the provided email and password match any user
        for user in users:
            if user["email"] == email and user["password"] == password:
                return True
        return False

    def create_lab(self, lab_id: str, name: str, nodes: list, email: str, password: str):
        """
        Creates a lab after authenticating the user.
        """
        # Authenticate the user
        if not self.authenticate(email, password):
            raise Exception("Authentication failed. Invalid email or password.")

        # Create a Lab instance with the provided data
        lab = Lab(id=lab_id, name=name, nodes=nodes)
        return self.client.request("POST", "/labs", json=lab.dict())

    def get_lab(self, lab_id: str, email: str, password: str):
        """
        Retrieves a lab's details after authenticating the user.
        """
        # Authenticate the user
        if not self.authenticate(email, password):
            raise Exception("Authentication failed. Invalid email or password.")

        # Fetch and return the lab details
        return self.client.request("GET", f"/labs/{lab_id}")
