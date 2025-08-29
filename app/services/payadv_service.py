import os
import uuid
from typing import Optional

import requests
from flask import current_app


class PayAdvantageClient:
    def __init__(self):
        self.api_key = current_app.config.get("PAYADV_API_KEY", "")
        self.public_key = current_app.config.get("PAYADV_PUBLIC_KEY", "")
        self.base_url = "https://api.payadvantage.com"  # placeholder

    def create_customer_and_authority(self, name: str, email: str, redirect_url: str) -> dict:
        # In a real integration, POST to Pay Advantage to create a hosted page session
        # Here we simulate by issuing a token and a hosted URL
        token = f"tok_{uuid.uuid4().hex}"
        hosted_url = f"{current_app.config['BASE_URL']}/hosted?token={token}&name={name}&email={email}&redirect={redirect_url}"
        return {
            "customer_id": f"cust_{uuid.uuid4().hex}",
            "token": token,
            "hosted_url": hosted_url,
        }

    def charge_with_token(self, token: str, amount_cents: int, reference: str) -> dict:
        # Simulate an API call; return success with a fake id
        payment_id = f"pay_{uuid.uuid4().hex}"
        return {
            "id": payment_id,
            "status": "success",
            "amount_cents": amount_cents,
            "reference": reference,
        }

