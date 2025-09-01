from datetime import date, timedelta, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os
import uuid
import requests
from sqlalchemy import func
from . import db
from .forms import PaymentScheduleForm
from .models import Booking, PaymentSchedule, Payment, XeroAuth
from .pay_advantage import PayAdvantageClient
from .xero_client import XeroClient

admin_bp = Blueprint("admin", __name__)


def _to_cents(amount_decimal) -> int:
	return int(round(float(amount_decimal) * 100))


@admin_bp.route("/")
@admin_bp.route("/bookings")
def bookings_list():
	bookings = Booking.query.filter_by(status="active").order_by(Booking.created_at.desc()).all()
	xero_auth = XeroAuth.query.first()
	return render_template("admin/bookings_list.html", bookings=bookings, xero_auth=xero_auth)


@admin_bp.route("/xero/connect")
def xero_connect():
	client_id = os.getenv("XERO_CLIENT_ID")
	client_secret = os.getenv("XERO_CLIENT_SECRET")
	redirect_uri = os.getenv("XERO_REDIRECT_URI", "http://localhost:5000/admin/xero/callback")
	if not client_id or not client_secret:
		flash("Xero client id/secret are not configured.", "danger")
		return redirect(url_for("admin.bookings_list"))

	scopes = os.getenv(
		"XERO_SCOPES",
		"offline_access accounting.transactions accounting.contacts",
	)
	state = uuid.uuid4().hex
	session["xero_oauth_state"] = state
	authorize_url = (
		"https://login.xero.com/identity/connect/authorize"
		+ "?response_type=code"
		+ f"&client_id={client_id}"
		+ f"&redirect_uri={redirect_uri}"
		+ f"&scope={requests.utils.quote(scopes)}"
		+ f"&state={state}"
	)
	return redirect(authorize_url)


@admin_bp.route("/xero/callback")
def xero_callback():
	code = request.args.get("code")
	state = request.args.get("state")
	stored_state = session.pop("xero_oauth_state", None)
	if not code:
		flash("Xero authorization failed: missing code.", "danger")
		return redirect(url_for("admin.bookings_list"))
	if not stored_state or stored_state != state:
		flash("Xero authorization failed: invalid state.", "danger")
		return redirect(url_for("admin.bookings_list"))

	client_id = os.getenv("XERO_CLIENT_ID")
	client_secret = os.getenv("XERO_CLIENT_SECRET")
	redirect_uri = os.getenv("XERO_REDIRECT_URI", "http://localhost:5000/admin/xero/callback")

	try:
		# Exchange code for tokens
		token_resp = requests.post(
			"https://identity.xero.com/connect/token",
			data={
				"grant_type": "authorization_code",
				"code": code,
				"redirect_uri": redirect_uri,
				"client_id": client_id,
				"client_secret": client_secret,
			},
			timeout=30,
		)
		token_resp.raise_for_status()
		payload = token_resp.json()
		access_token = payload.get("access_token")
		refresh_token = payload.get("refresh_token")
		expires_in = int(payload.get("expires_in", 1800))
		scope = payload.get("scope")
		if not access_token or not refresh_token:
			raise RuntimeError("Missing tokens in Xero response")

		# Get tenant (connection)
		conn_resp = requests.get(
			"https://api.xero.com/connections",
			headers={"Authorization": f"Bearer {access_token}"},
			timeout=30,
		)
		conn_resp.raise_for_status()
		connections = conn_resp.json() or []
		if not connections:
			raise RuntimeError("No Xero tenants authorized for this connection")
		tenant_id = connections[0].get("tenantId")
		if not tenant_id:
			raise RuntimeError("Missing tenantId in Xero connections response")

		expires_at = datetime.utcnow() + timedelta(seconds=expires_in - 60)
		xero_auth = XeroAuth.query.first()
		if not xero_auth:
			xero_auth = XeroAuth()
			db.session.add(xero_auth)
		xero_auth.tenant_id = tenant_id
		xero_auth.access_token = access_token
		xero_auth.refresh_token = refresh_token
		xero_auth.access_token_expires_at = expires_at
		xero_auth.scope = scope
		db.session.commit()
		flash("Xero connected successfully.", "success")
	except Exception as exc:
		flash(f"Failed to connect Xero: {exc}", "danger")

	return redirect(url_for("admin.bookings_list"))


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

		# Create payment schedule with Pay Advantage v3
		try:
			schedule_resp = client.create_direct_debit_schedule(
				customer_name=booking.customer_name,
				email=booking.email,
				phone=booking.phone,
				recurring_amount_cents=recurring_cents,
				frequency=frequency,
				description=form.description.data,
				recurring_date_start=form.recurring_date_start.data,
				reminder_days=form.reminder_days.data,
				upfront_amount_cents=upfront_cents,
			)
		except requests.HTTPError as exc:
			provider_msg = None
			if getattr(exc, "response", None) is not None:
				try:
					provider_msg = exc.response.json()
				except Exception:
					provider_msg = exc.response.text
			flash(f"PayAdvantage error: {exc} | Details: {provider_msg}", "danger")
			return render_template("admin/edit_booking.html", booking=booking, form=form)
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
		if booking.payment_schedule.next_debit_date:
			form.recurring_date_start.data = booking.payment_schedule.next_debit_date

	return render_template("admin/edit_booking.html", booking=booking, form=form)


@admin_bp.route("/bookings/<int:booking_id>/payments")
def view_payments(booking_id: int):
	booking = Booking.query.get_or_404(booking_id)
	payments = booking.payments
	return render_template("admin/payments.html", booking=booking, payments=payments)