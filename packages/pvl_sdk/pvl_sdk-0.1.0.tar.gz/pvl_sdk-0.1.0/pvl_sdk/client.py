import requests


class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def request(self, method: str, endpoint: str, **kwargs):
        url = f"{self.base_url}{endpoint}"
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()  # Raise HTTPError for bad responses
        return response.json()
