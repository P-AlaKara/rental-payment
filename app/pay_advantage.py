import os
import uuid
import requests
from requests.auth import HTTPBasicAuth


class PayAdvantageClient:
	def __init__(self):
		self.base_url = os.getenv("PAYADVANTAGE_BASE_URL", "https://api.sandbox.payadvantage.com")
		self.api_key = os.getenv("PAYADVANTAGE_API_KEY")
		self.username = os.getenv("PAYADVANTAGE_USERNAME")
		self.password = os.getenv("PAYADVANTAGE_PASSWORD")

	def create_direct_debit_schedule(self, customer_name: str, email: str, phone: str, recurring_amount_cents: int, frequency: str) -> dict:
		# Determine authentication strategy: API key or basic auth with username/password
		if not self.api_key and not (self.username and self.password):
			raise RuntimeError(
				"Configure PAYADVANTAGE_API_KEY or PAYADVANTAGE_USERNAME and PAYADVANTAGE_PASSWORD"
			)

		headers = {
			"Content-Type": "application/json",
			"Accept": "application/json",
		}
		if self.api_key:
			headers["Authorization"] = f"Bearer {self.api_key}"

		auth = None
		if not self.api_key and self.username and self.password:
			auth = HTTPBasicAuth(self.username, self.password)

		response = requests.post(
			f"{self.base_url}/direct-debits/schedules",
			headers=headers,
			auth=auth,
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