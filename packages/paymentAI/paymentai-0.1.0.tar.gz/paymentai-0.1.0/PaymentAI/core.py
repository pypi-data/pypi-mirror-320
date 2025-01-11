import requests

def transaction(event_name: str, data: dict, endpoint_url: str) -> dict:
    
    payload = {
        "event": event_name,
        "data": data
    }

    try:
        response = requests.post(endpoint_url, json=payload)
        response.raise_for_status()
        return {"status": "success", "response": response.json()}
    except requests.RequestException as e:
        return {"status": "failure", "error": str(e)}
