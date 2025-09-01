import os
import uuid
import logging
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
		self.logger = logging.getLogger(__name__)

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

		# Log which auth path is used (without secrets)
		auth_mode = "api_key" if self.api_key else ("basic" if auth else "none")
		self.logger.info(
			"PayAdvantage request: POST %s, auth=%s",
			f"{self.base_url}/v3/direct_debits",
			auth_mode,
		)

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
		if not response.ok:
			# Try to surface provider error message
			try:
				body_obj = response.json()
			except Exception:
				body_obj = response.text
			self.logger.error(
				"PayAdvantage error: status=%s body=%s",
				response.status_code,
				body_obj,
			)
			message = None
			if isinstance(body_obj, dict):
				message = body_obj.get("message") or body_obj.get("error") or str(body_obj)
			else:
				message = str(body_obj)
			raise requests.HTTPError(
				f"PayAdvantage {response.status_code}: {message}", response=response
			)
		return response.json()