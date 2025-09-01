import os
import uuid
from datetime import date
import requests
from requests.auth import HTTPBasicAuth


class PayAdvantageClient:
	def __init__(self):
		# Default to production AU domain; override via PAYADVANTAGE_BASE_URL
		# For test, use https://api.test.payadvantage.com.au
		self.base_url = os.getenv("PAYADVANTAGE_BASE_URL", "https://api.payadvantage.com.au")
		self.api_key = os.getenv("PAYADVANTAGE_API_KEY")
		self.username = os.getenv("PAYADVANTAGE_USERNAME")
		self.password = os.getenv("PAYADVANTAGE_PASSWORD")

	def create_direct_debit_schedule(
		self,
		customer_name: str,
		email: str,
		phone: str,
		recurring_amount_cents: int,
		frequency: str,
		description: str,
		recurring_date_start: date,
		reminder_days: int,
		upfront_amount_cents: int = 0,
	) -> dict:
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

		# Convert cents to dollars as per v3 API
		recurring_amount = round(recurring_amount_cents / 100.0, 2)
		upfront_amount = round(upfront_amount_cents / 100.0, 2) if upfront_amount_cents and upfront_amount_cents > 0 else None

		payload = {
			"Customer": {"Name": customer_name, "Email": email, "Mobile": phone},
			"Description": description,
			"RecurringAmount": recurring_amount,
			"RecurringDateStart": recurring_date_start.isoformat(),
			"Frequency": frequency,
			"ReminderDays": int(reminder_days),
		}
		if upfront_amount is not None:
			payload["UpfrontAmount"] = upfront_amount

		response = requests.post(
			f"{self.base_url}/v3/direct_debits",
			headers=headers,
			auth=auth,
			json=payload,
			timeout=30,
		)
		response.raise_for_status()
		return response.json()