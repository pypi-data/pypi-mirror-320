from typing import List
import requests


class DXRHttpClient:
    """
    A singleton HTTP client for interacting with the DXR API.
    """

    _instance = None

    def __init__(self, api_url: str, api_key: str):
        """
        Initialize the DXRHttpClient with the given API URL and API key.

        :param api_url: The base URL of the DXR API.
        :param api_key: The API key for authentication.
        """
        self.api_url = api_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        )

    @classmethod
    def get_instance(
        cls, api_url: str | None = None, api_key: str | None = None
    ) -> "DXRHttpClient":
        """
        Get the singleton instance of the DXRHttpClient. If it does not exist, create it.

        :param api_url: The base URL of the DXR API (required for first initialization).
        :param api_key: The API key for authentication (required for first initialization).
        :return: The singleton instance of DXRHttpClient.
        :raises ValueError: If the instance is not initialized and API URL or API key is not provided.
        """
        if cls._instance is None:
            if not api_url or not api_key:
                raise ValueError(
                    "API URL and API key must be provided for the first initialization."
                )
            cls._instance = cls(api_url, api_key)
        return cls._instance

    def request(self, method: str, endpoint: str, **kwargs) -> dict:
        """
        Make an HTTP request to the DXR API.

        :param method: The HTTP method (e.g., 'GET', 'POST').
        :param endpoint: The API endpoint to call.
        :param kwargs: Additional arguments to pass to the request.
        :return: The JSON response from the API.
        :raises requests.exceptions.HTTPError: If the HTTP request returned an unsuccessful status code.
        """
        if not self.api_url.endswith("/"):
            self.api_url += "/"
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]

        url = f"{self.api_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def update_headers(self, headers: dict) -> None:
        """
        Update the headers for the HTTP session.

        :param headers: A dictionary of headers to update.
        """
        self.session.headers.update(headers)

    def get(self, url: str, **kwargs) -> dict:
        """
        Make a GET request to the DXR API.

        :param url: The API endpoint to call.
        :param kwargs: Additional arguments to pass to the request.
        :return: The JSON response from the API.
        """
        return self.request("GET", url, **kwargs)

    def post(self, url: str, files: List[tuple] | None = None, **kwargs) -> dict:
        """
        Make a POST request to the DXR API.

        :param url: The API endpoint to call.
        :param files: Files to include in the POST request.
        :param kwargs: Additional arguments to pass to the request.
        :return: The JSON response from the API.
        """
        if files:
            # Remove the content type override - let requests handle it
            kwargs["files"] = files

            # Remove Content-Type header to allow 'multipart/form-data'
            if "Content-Type" in self.session.headers:
                del self.session.headers["Content-Type"]

        return self.request("POST", url, **kwargs)
