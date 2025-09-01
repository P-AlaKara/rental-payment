import os
import uuid


class XeroClient:
	def __init__(self):
		self.base_url = os.getenv("XERO_BASE_URL", "https://api.sandbox.xero.com")
		self.api_key = os.getenv("XERO_API_KEY", "stub-key")

	def create_invoice(self, contact_name: str, email: str, amount_cents: int, due_date, description: str) -> dict:
		# Stub response; replace with real Xero API call
		return {
			"invoice_id": str(uuid.uuid4()),
			"status": "DRAFT",
			"amount_cents": amount_cents,
			"due_date": due_date.isoformat(),
			"description": description,
			"to": {"name": contact_name, "email": email},
		}