from datetime import date, timedelta
from flask import Flask
from apscheduler.schedulers.base import BaseScheduler
from . import db
from .models import Payment, PaymentSchedule
from .xero_client import XeroClient


def _currency(amount_cents: int) -> float:
	return round(amount_cents / 100.0, 2)


def schedule_jobs(scheduler: BaseScheduler, app: Flask) -> None:
	# Runs daily at 01:00 UTC to create invoices 2 days before debit
	scheduler.add_job(
		func=_create_invoices_for_upcoming_payments,
		trigger="cron",
		hour=1,
		minute=0,
		args=[app],
		id="create_invoices_2_days_prior",
		replace_existing=True,
	)
	# Runs daily at 02:00 UTC to mark overdue payments
	scheduler.add_job(
		func=_mark_overdue_payments,
		trigger="cron",
		hour=2,
		minute=0,
		args=[app],
		id="mark_overdue_payments",
		replace_existing=True,
	)


def _create_invoices_for_upcoming_payments(app: Flask):
	with app.app_context():
		client = XeroClient()
		today = date.today()
		not_before = today + timedelta(days=2)
		pending = (
			Payment.query.filter(
				Payment.status == "pending",
				Payment.scheduled_date == not_before,
				Payment.invoice_id.is_(None),
			)
			.all()
		)
		for payment in pending:
			booking = payment.booking
			invoice = client.create_invoice(
				contact_name=booking.customer_name,
				email=booking.email,
				amount_cents=payment.scheduled_amount_cents,
				due_date=payment.scheduled_date,
				description=f"Recurring debit for booking #{booking.id} on {payment.scheduled_date.isoformat()} ({_currency(payment.scheduled_amount_cents)})",
			)
			payment.invoice_id = invoice.get("invoice_id")
		db.session.commit()


def _mark_overdue_payments(app: Flask):
	with app.app_context():
		today = date.today()
		to_overdue = Payment.query.filter(
			Payment.status == "pending",
			Payment.scheduled_date < today,
		).all()
		for payment in to_overdue:
			payment.status = "overdue"
		db.session.commit()