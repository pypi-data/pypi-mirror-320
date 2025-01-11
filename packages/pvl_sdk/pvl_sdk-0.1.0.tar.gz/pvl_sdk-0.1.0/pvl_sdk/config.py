from .client import APIClient


class ConfigAPI:
    def __init__(self, client: APIClient):
        self.client = client

    def update_config(self, node_id: str, config_data: dict):
        data = {"node_id": node_id, "config_data": config_data}
        return self.client.request("POST", "/config", json=data)
