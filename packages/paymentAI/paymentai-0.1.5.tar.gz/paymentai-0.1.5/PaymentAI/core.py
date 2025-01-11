import requests
import os

DEFAULT_ENDPOINT_URL = "https://api.agentpaid.io"

def transaction(event_name: str, data: dict) -> dict:
    """
    Sends a transaction to the specified endpoint.
    
    Parameters:
        event_name (str): The name of the event.
        data (dict): The data associated with the event.
        endpoint_url (str, optional): The URL to send the request to. Defaults to `DEFAULT_ENDPOINT_URL`.
    
    Returns:
        dict: The response status and data.
    """
    endpoint_url = os.getenv("TRANSACTION_ENDPOINT_URL", DEFAULT_ENDPOINT_URL)
    
    payload = {
        "event_name": event_name,
        "data": data
    }

    try:
        response = requests.post(endpoint_url + '/entries', json=payload)
        response.raise_for_status()
        return {"status": "success"}
    except requests.RequestException as e:
        return {"status": "failure", "error": str(e)}
