import json
from datetime import datetime, timedelta
from typing import Optional

import requests
from flask import current_app
from .. import db
from ..models import XeroAuth


def _get_stored_auth() -> Optional[XeroAuth]:
    return XeroAuth.query.first()


def _save_auth(token: dict, tenant_id: Optional[str] = None) -> XeroAuth:
    expires_at = None
    if token.get("expires_in"):
        expires_at = datetime.utcnow() + timedelta(seconds=int(token["expires_in"]))
    row = _get_stored_auth() or XeroAuth(
        access_token=token.get("access_token", ""),
        refresh_token=token.get("refresh_token"),
        token_type=token.get("token_type"),
        scope=token.get("scope"),
        expires_at=expires_at,
        tenant_id=tenant_id,
    )
    if row.id:
        row.access_token = token.get("access_token", row.access_token)
        row.refresh_token = token.get("refresh_token", row.refresh_token)
        row.token_type = token.get("token_type", row.token_type)
        row.scope = token.get("scope", row.scope)
        row.expires_at = expires_at or row.expires_at
        row.tenant_id = tenant_id or row.tenant_id
    db.session.add(row)
    db.session.commit()
    return row


def get_valid_access_token() -> Optional[str]:
    row = _get_stored_auth()
    if not row:
        return None
    if not row.expires_at or row.expires_at <= datetime.utcnow() + timedelta(seconds=60):
        client_id = current_app.config.get("XERO_CLIENT_ID")
        client_secret = current_app.config.get("XERO_CLIENT_SECRET")
        data = {
            "grant_type": "refresh_token",
            "refresh_token": row.refresh_token,
        }
        resp = requests.post(
            "https://identity.xero.com/connect/token",
            data=data,
            auth=(client_id, client_secret),
            timeout=30,
        )
        resp.raise_for_status()
        token = resp.json()
        _save_auth(token)
        row = _get_stored_auth()
    return row.access_token


def get_tenant_id() -> Optional[str]:
    configured = current_app.config.get("XERO_TENANT_ID")
    if configured:
        return configured
    row = _get_stored_auth()
    return row.tenant_id if row else None


class XeroClient:
    def __init__(self):
        self.client_id = current_app.config.get("XERO_CLIENT_ID")
        self.client_secret = current_app.config.get("XERO_CLIENT_SECRET")
        self.tenant_id = current_app.config.get("XERO_TENANT_ID")

    def create_and_approve_invoice(self, contact_name: str, contact_email: str, amount_cents: int, reference: str) -> dict:
        access_token = get_valid_access_token()
        tenant_id = self.tenant_id or get_tenant_id()
        if not access_token or not tenant_id:
            raise RuntimeError("Xero not authorized. Please connect once via /xero/connect")

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Xero-tenant-id": tenant_id,
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

