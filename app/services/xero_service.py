import uuid
from typing import Optional

from flask import current_app


class XeroClient:
    def __init__(self):
        self.client_id = current_app.config.get("XERO_CLIENT_ID")
        self.client_secret = current_app.config.get("XERO_CLIENT_SECRET")
        self.tenant_id = current_app.config.get("XERO_TENANT_ID")

    def create_and_approve_invoice(self, contact_name: str, contact_email: str, amount_cents: int, reference: str) -> dict:
        # Simulate creating an approved invoice in Xero
        xero_invoice_id = f"inv_{uuid.uuid4().hex}"
        return {
            "id": xero_invoice_id,
            "status": "APPROVED",
            "amount_cents": amount_cents,
            "reference": reference,
            "contact": {"name": contact_name, "email": contact_email},
        }

