import os
import uuid
from datetime import datetime, timedelta
import requests
from . import db
from .models import XeroAuth


class XeroClient:
	def __init__(self):
		self.identity_url = "https://identity.xero.com/connect/token"
		self.api_base = os.getenv("XERO_API_BASE", "https://api.xero.com/api.xro/2.0")
		self.client_id = os.getenv("XERO_CLIENT_ID")
		self.client_secret = os.getenv("XERO_CLIENT_SECRET")
		self.sales_account_code = os.getenv("XERO_SALES_ACCOUNT_CODE", "200")

	def _get_auth_row(self) -> XeroAuth:
		xero_auth = XeroAuth.query.first()
		if not xero_auth or not xero_auth.refresh_token or not xero_auth.tenant_id:
			raise RuntimeError("Xero is not connected. Please connect in Admin.")
		return xero_auth

	def _ensure_access_token(self) -> tuple[str, str]:
		xero_auth = self._get_auth_row()
		# If token missing or expired, refresh
		if (
			not xero_auth.access_token
			or not xero_auth.access_token_expires_at
			or xero_auth.access_token_expires_at <= datetime.utcnow()
		):
			resp = requests.post(
				self.identity_url,
				data={
					"grant_type": "refresh_token",
					"refresh_token": xero_auth.refresh_token,
					"client_id": self.client_id,
					"client_secret": self.client_secret,
				},
				timeout=30,
			)
			resp.raise_for_status()
			data = resp.json()
			xero_auth.access_token = data.get("access_token")
			xero_auth.refresh_token = data.get("refresh_token", xero_auth.refresh_token)
			expires_in = int(data.get("expires_in", 1800))
			xero_auth.access_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)
			xero_auth.scope = data.get("scope", xero_auth.scope)
			db.session.commit()
		return xero_auth.access_token, xero_auth.tenant_id

	def create_invoice(self, contact_name: str, email: str, amount_cents: int, due_date, description: str) -> dict:
		access_token, tenant_id = self._ensure_access_token()
		amount = round(amount_cents / 100.0, 2)
		payload = {
			"Type": "ACCREC",
			"Contact": {
				"Name": contact_name,
				"EmailAddress": email,
			},
			"Date": datetime.utcnow().date().isoformat(),
			"DueDate": due_date.isoformat(),
			"LineAmountTypes": "Exclusive",
			"LineItems": [
				{
					"Description": description,
					"Quantity": 1.0,
					"UnitAmount": amount,
					"AccountCode": self.sales_account_code,
				}
			],
			"Status": "DRAFT",
		}
		resp = requests.post(
			f"{self.api_base}/Invoices",
			headers={
				"Authorization": f"Bearer {access_token}",
				"Xero-tenant-id": tenant_id,
				"Accept": "application/json",
				"Content-Type": "application/json",
			},
			json={"Invoices": [payload]},
			timeout=30,
		)
		resp.raise_for_status()
		data = resp.json()
		invoice = (data.get("Invoices") or [{}])[0]
		invoice_id = invoice.get("InvoiceID") or str(uuid.uuid4())
		return {
			"invoice_id": invoice_id,
			"status": invoice.get("Status", "DRAFT"),
			"amount_cents": amount_cents,
			"due_date": due_date.isoformat(),
			"description": description,
			"to": {"name": contact_name, "email": email},
		}