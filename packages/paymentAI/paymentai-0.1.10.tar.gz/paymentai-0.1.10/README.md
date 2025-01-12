# PaymentAI

A Python client for interacting with the AgentPaid API. This package allows you to send transaction events to the API.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install PaymentAI.

```bash
pip install paymentAI
```

## Usage

```python
from PaymentAI import Client

# Initialize with API token (and custom endpoint if necessary)
api_token = "your_api_token_here"
client = Client(api_token)

# Prepare data for the event
data = {
    "event_name": "bbc_summary",
    "agent_id" : "xx",
    "customer_id" : "xx",
    "foo": "bar"
}

# Send the transaction
response = client.send_transaction(data)
```