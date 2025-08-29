import os
import uuid
from typing import Optional

import requests
from flask import current_app


class PayAdvantageClient:
    def __init__(self):
        self.api_key = current_app.config.get("PAYADV_API_KEY", "")
        self.public_key = current_app.config.get("PAYADV_PUBLIC_KEY", "")
        self.base_url = current_app.config.get("PAYADV_BASE_URL", "https://api.payadvantage.com.au")
        self.hosted_url = current_app.config.get("PAYADV_HOSTED_URL", "https://portal.payadvantage.com.au")

    def create_customer_and_authority(self, name: str, email: str, redirect_url: str) -> dict:
        # Real-world outline (replace with actual Pay Advantage endpoints):
        # 1) Create or upsert customer at Pay Advantage (if required)
        # 2) Create a hosted payment authority session; Pay Advantage returns a redirect URL
        # Fallback: redirect to configured hosted URL which will redirect back with token
        session_id = uuid.uuid4().hex
        hosted_url = (
            f"{self.hosted_url}/hosted/authority?session={session_id}"
            f"&name={requests.utils.quote(name)}&email={requests.utils.quote(email)}"
            f"&redirect={requests.utils.quote(redirect_url)}"
        )
        return {
            "customer_id": f"cust_{uuid.uuid4().hex}",
            "session_id": session_id,
            "hosted_url": hosted_url,
        }

    def charge_with_token(self, token: str, amount_cents: int, reference: str) -> dict:
        # Replace with a POST to Pay Advantage charge endpoint using stored token
        payment_id = f"pay_{uuid.uuid4().hex}"
        return {
            "id": payment_id,
            "status": "success",
            "amount_cents": amount_cents,
            "reference": reference,
        }

