import os
import uuid
from typing import Optional

import requests
from flask import current_app


class PayAdvantageClient:
    def __init__(self):
        self.username = current_app.config.get("PAYADV_USERNAME", "")
        self.password = current_app.config.get("PAYADV_PASSWORD", "")
        self.base_url = current_app.config.get("PAYADV_BASE_URL", "https://api.payadvantage.com.au")
        self.hosted_url = current_app.config.get("PAYADV_HOSTED_URL", "https://portal.payadvantage.com.au")

    def create_customer_and_authority(self, name: str, email: str, redirect_url: str) -> dict:
        # Real-world outline (replace with actual Pay Advantage endpoints):
        # 1) Create or upsert customer at Pay Advantage (if required)
        # 2) Create a hosted payment authority session; Pay Advantage returns a redirect URL
        # Fallback: redirect to configured hosted URL which will redirect back with token
        # Example POST with Basic Auth to create hosted authority session (replace endpoint/path):
        # resp = requests.post(
        #     f"{self.base_url}/v1/hosted/authorities",
        #     json={"name": name, "email": email, "redirect_url": redirect_url},
        #     auth=(self.username, self.password),
        #     timeout=30,
        # )
        # resp.raise_for_status()
        # data = resp.json()
        # return {"customer_id": data["customer_id"], "session_id": data["session_id"], "hosted_url": data["url"]}

        # Placeholder fallback if endpoint not available: use simulated hosted page
        session_id = uuid.uuid4().hex
        hosted_url = (
            f"{current_app.config['BASE_URL']}/hosted?token={session_id}"
            f"&name={requests.utils.quote(name)}&email={requests.utils.quote(email)}"
            f"&redirect={requests.utils.quote(redirect_url)}"
        )
        return {"customer_id": f"cust_{uuid.uuid4().hex}", "session_id": session_id, "hosted_url": hosted_url}

    def create_direct_debit_link(self, name: str, email: str, mobile: str, reference: str, redirect_url: str) -> dict:
        """
        Use Pay Advantage 'Create a new Direct Debit' to generate a hosted link
        that the customer can use to complete the DDR authorization.
        """
        # Example real call (replace with exact schema/fields required by Pay Advantage):
        # payload = {
        #     "customer": {
        #         "name": name,
        #         "email": email,
        #         "mobile": mobile,
        #     },
        #     "reference": reference,
        #     "redirect_url": redirect_url,
        # }
        # resp = requests.post(
        #     f"{self.base_url}/v3/direct_debits",
        #     json=payload,
        #     auth=(self.username, self.password),
        #     timeout=30,
        # )
        # resp.raise_for_status()
        # data = resp.json()
        # return {"hosted_url": data["link"], "ddr_id": data["id"]}

        # Placeholder fallback for local testing
        session_id = uuid.uuid4().hex
        hosted_url = (
            f"{current_app.config['BASE_URL']}/hosted?token={session_id}"
            f"&name={requests.utils.quote(name)}&email={requests.utils.quote(email)}"
            f"&redirect={requests.utils.quote(redirect_url)}"
        )
        return {"hosted_url": hosted_url, "ddr_id": session_id}

    def charge_with_token(self, token: str, amount_cents: int, reference: str) -> dict:
        # Example POST with Basic Auth to charge using stored token (replace endpoint/path):
        # resp = requests.post(
        #     f"{self.base_url}/v1/payments",
        #     json={"token": token, "amount": amount_cents, "reference": reference},
        #     auth=(self.username, self.password),
        #     timeout=30,
        # )
        # resp.raise_for_status()
        # data = resp.json()
        # return {"id": data["id"], "status": data["status"], "amount_cents": amount_cents, "reference": reference}

        # Placeholder simulated success
        payment_id = f"pay_{uuid.uuid4().hex}"
        return {"id": payment_id, "status": "success", "amount_cents": amount_cents, "reference": reference}

