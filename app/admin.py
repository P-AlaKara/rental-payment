from datetime import date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import func
from . import db
from .forms import PaymentScheduleForm
from .models import Booking, PaymentSchedule, Payment
from .pay_advantage import PayAdvantageClient
from .xero_client import XeroClient

admin_bp = Blueprint("admin", __name__)


def _to_cents(amount_decimal) -> int:
	return int(round(float(amount_decimal) * 100))


@admin_bp.route("/")
@admin_bp.route("/bookings")
def bookings_list():
	bookings = Booking.query.filter_by(status="active").order_by(Booking.created_at.desc()).all()
	return render_template("admin/bookings_list.html", bookings=bookings)


@admin_bp.route("/report")
def report():
	total_active = Booking.query.filter_by(status="active").count()
	payments_summary = db.session.query(
		Payment.status,
		func.count(Payment.id),
		func.coalesce(func.sum(Payment.scheduled_amount_cents), 0),
		func.coalesce(func.sum(Payment.paid_amount_cents), 0),
	).group_by(Payment.status).all()
	# Transform into dict for template ease
	summary = {row[0]: {"count": row[1], "scheduled_sum": row[2], "paid_sum": row[3]} for row in payments_summary}
	return render_template("admin/report.html", total_active=total_active, summary=summary)


@admin_bp.route("/bookings/<int:booking_id>/edit", methods=["GET", "POST"])
def edit_booking(booking_id: int):
	booking = Booking.query.get_or_404(booking_id)
	form = PaymentScheduleForm()
	client = PayAdvantageClient()
	xero = XeroClient()

	if form.validate_on_submit():
		upfront_cents = _to_cents(form.upfront_amount.data)
		recurring_cents = _to_cents(form.recurring_amount.data)
		frequency = form.frequency.data

		# Create payment schedule with Pay Advantage (stub)
		schedule_resp = client.create_direct_debit_schedule(
			customer_name=booking.customer_name,
			email=booking.email,
			phone=booking.phone,
			recurring_amount_cents=recurring_cents,
			frequency=frequency,
		)
		provider_schedule_id = schedule_resp.get("schedule_id")

		# Store schedule
		schedule = booking.payment_schedule or PaymentSchedule(booking_id=booking.id)
		schedule.upfront_amount_cents = upfront_cents
		schedule.recurring_amount_cents = recurring_cents
		schedule.frequency = frequency
		schedule.provider_schedule_id = provider_schedule_id
		# For demonstration, set next debit in 7/14/30 days
		if frequency == "weekly":
			schedule.next_debit_date = date.today() + timedelta(days=7)
		elif frequency == "fortnightly":
			schedule.next_debit_date = date.today() + timedelta(days=14)
		else:
			schedule.next_debit_date = date.today() + timedelta(days=30)
		db.session.add(schedule)
		db.session.commit()

		# Create upfront invoice via Xero (stub)
		if upfront_cents > 0:
			invoice = xero.create_invoice(
				contact_name=booking.customer_name,
				email=booking.email,
				amount_cents=upfront_cents,
				due_date=date.today(),
				description=f"Upfront payment for booking #{booking.id}",
			)
			upfront_payment = Payment(
				booking_id=booking.id,
				scheduled_date=date.today(),
				scheduled_amount_cents=upfront_cents,
				status="pending",
				invoice_id=invoice.get("invoice_id"),
			)
			db.session.add(upfront_payment)

		# Seed the first recurring payment row (subsequent ones could be added by webhook or scheduler)
		first_recurring = Payment(
			booking_id=booking.id,
			scheduled_date=schedule.next_debit_date,
			scheduled_amount_cents=recurring_cents,
			status="pending",
		)
		db.session.add(first_recurring)
		db.session.commit()

		flash("Direct debit schedule set and upfront invoice created.", "success")
		return redirect(url_for("admin.bookings_list"))

	# Pre-fill if schedule exists
	if request.method == "GET" and booking.payment_schedule:
		form.upfront_amount.data = booking.payment_schedule.upfront_amount_cents / 100.0
		form.recurring_amount.data = booking.payment_schedule.recurring_amount_cents / 100.0
		form.frequency.data = booking.payment_schedule.frequency

	return render_template("admin/edit_booking.html", booking=booking, form=form)


@admin_bp.route("/bookings/<int:booking_id>/payments")
def view_payments(booking_id: int):
	booking = Booking.query.get_or_404(booking_id)
	payments = booking.payments
	return render_template("admin/payments.html", booking=booking, payments=payments)