from .client import APIClient
from .nodes import NodesAPI
from .labs import LabsAPI
from .config import ConfigAPI


class SDK:
    def __init__(self, base_url: str):
        self.client = APIClient(base_url)
        self.nodes = NodesAPI(self.client)
        self.labs = LabsAPI(self.client)
        self.config = ConfigAPI(self.client)
