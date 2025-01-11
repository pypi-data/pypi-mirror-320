# from .client import APIClient
# from .models import Node


# class NodesAPI:
#     def __init__(self, client: APIClient):
#         self.client = client

#     def create_node(self, node_id: str, name: str, interfaces: list):
#         # Create a Node instance with the provided data
#         node = Node(id=node_id, name=name, interfaces=interfaces)
#         # data = {"id": node_id, "name": name, "interfaces": interfaces}
#         return self.client.request("POST", "/nodes", json=node.dict())

#     def list_nodes(self):
#         return self.client.request("GET", "/nodes")

import json
from .client import APIClient
from .models import Node

class NodesAPI:
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

    def create_node(self, node_id: str, name: str, interfaces: list, email: str, password: str):
        """
        Creates a node after authenticating the user.
        """
        # Authenticate the user
        if not self.authenticate(email, password):
            raise Exception("Authentication failed. Invalid email or password.")

        # Create a Node instance with the provided data
        node = Node(id=node_id, name=name, interfaces=interfaces)
        return self.client.request("POST", "/nodes", json=node.dict())

    def list_nodes(self, email: str, password: str):
        """
        Lists all nodes after authenticating the user.
        """
        # Authenticate the user
        if not self.authenticate(email, password):
            raise Exception("Authentication failed. Invalid email or password.")
        
        # Fetch and return the list of nodes
        return self.client.request("GET", "/nodes")
