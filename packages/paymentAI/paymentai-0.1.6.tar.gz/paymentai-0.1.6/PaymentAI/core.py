import requests
import logging

DEFAULT_ENDPOINT_URL = "https://api.agentpaid.io"

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Client:
    """
    A client for interacting with the AgentPaid API.
    """

    def __init__(self, api_token: str, endpoint_url: str = DEFAULT_ENDPOINT_URL):
        """
        Initialize the client with an API token and optional endpoint URL.
        """
        if not api_token:
            raise ValueError("API token is required to initialize the client.")
        self.api_token = api_token
        self.endpoint_url = endpoint_url.rstrip('/') 
        logger.info(f"Client initialized with endpoint: {self.endpoint_url}")

    def send_transaction(self, event_name: str, data: dict) -> dict:
        """
        Send a transaction event to the API.
        """
        if not event_name:
            raise ValueError("Event name cannot be empty.")
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary.")

        payload = {
            "event_name": event_name,
            "data": data,
        }

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                f"{self.endpoint_url}/entries",
                json=payload,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            logger.info(f"Transaction succeeded: {response.status_code}")
            return {"status": "success", "response": response.json()}
        except requests.RequestException as e:
            logger.error(f"Transaction failed: {str(e)}")
            return {"status": "failure", "error": str(e)}
