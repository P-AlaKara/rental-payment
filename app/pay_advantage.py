import os
import uuid
import requests


class PayAdvantageClient:
	def __init__(self):
		self.base_url = os.getenv("PAYADVANTAGE_BASE_URL", "https://api.sandbox.payadvantage.com")
		self.api_key = os.getenv("PAYADVANTAGE_API_KEY", "stub-key")

	def create_direct_debit_schedule(self, customer_name: str, email: str, phone: str, recurring_amount_cents: int, frequency: str) -> dict:
		# Stub response for development; replace with real POST request using requests
		# Example (commented):
		# response = requests.post(
		#     f"{self.base_url}/direct-debits/schedules",
		#     headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
		#     json={
		#         "customer": {"name": customer_name, "email": email, "phone": phone},
		#         "recurring_amount_cents": recurring_amount_cents,
		#         "frequency": frequency,
		#         "redirect_url": os.getenv("PAYADVANTAGE_REDIRECT_URL", "http://localhost:5000/admin/bookings"),
		#     },
		#     timeout=20,
		# )
		# response.raise_for_status()
		# return response.json()
		return {"schedule_id": str(uuid.uuid4()), "authorization_url": "https://example.com/authorize"}