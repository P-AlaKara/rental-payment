import json
from typing import Optional

import requests
from flask import current_app


class XeroClient:
    def __init__(self):
        self.client_id = current_app.config.get("XERO_CLIENT_ID")
        self.client_secret = current_app.config.get("XERO_CLIENT_SECRET")
        self.tenant_id = current_app.config.get("XERO_TENANT_ID")

    def create_and_approve_invoice(self, contact_name: str, contact_email: str, amount_cents: int, reference: str, access_token: str) -> dict:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Xero-tenant-id": self.tenant_id,
            "Content-Type": "application/json",
        }
        invoice_payload = {
            "Type": "ACCREC",
            "Contact": {"Name": contact_name, "EmailAddress": contact_email},
            "LineItems": [
                {
                    "Description": f"Car Rental {reference}",
                    "Quantity": 1,
                    "UnitAmount": round(amount_cents / 100.0, 2),
                    "AccountCode": "200",
                }
            ],
            "Status": "AUTHORISED",
            "Reference": reference,
        }
        resp = requests.post(
            "https://api.xero.com/api.xro/2.0/Invoices",
            headers=headers,
            data=json.dumps({"Invoices": [invoice_payload]}),
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        inv = data.get("Invoices", [{}])[0]
        return {"id": inv.get("InvoiceID"), "status": inv.get("Status"), "amount_cents": amount_cents, "reference": reference}

