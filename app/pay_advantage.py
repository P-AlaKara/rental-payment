import os
import uuid
import requests


class PayAdvantageClient:
	def __init__(self):
		self.base_url = os.getenv("PAYADVANTAGE_BASE_URL", "https://api.sandbox.payadvantage.com")
		self.api_key = os.getenv("PAYADVANTAGE_API_KEY")

	def create_direct_debit_schedule(self, customer_name: str, email: str, phone: str, recurring_amount_cents: int, frequency: str) -> dict:
		if not self.api_key:
			raise RuntimeError("PAYADVANTAGE_API_KEY is not configured")
		response = requests.post(
			f"{self.base_url}/direct-debits/schedules",
			headers={
				"Authorization": f"Bearer {self.api_key}",
				"Content-Type": "application/json",
				"Accept": "application/json",
			},
			json={
				"customer": {"name": customer_name, "email": email, "phone": phone},
				"recurring_amount_cents": recurring_amount_cents,
				"frequency": frequency,
				"redirect_url": os.getenv("PAYADVANTAGE_REDIRECT_URL", "http://localhost:5000/admin/bookings"),
			},
			timeout=30,
		)
		response.raise_for_status()
		return response.json()