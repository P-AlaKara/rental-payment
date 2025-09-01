from datetime import datetime, date
from typing import Optional
from . import db


class Booking(db.Model):
	__tablename__ = "bookings"

	id = db.Column(db.Integer, primary_key=True)
	customer_name = db.Column(db.String(120), nullable=False)
	email = db.Column(db.String(200), nullable=False)
	phone = db.Column(db.String(50), nullable=False)
	start_date = db.Column(db.Date, nullable=False)
	end_date = db.Column(db.Date, nullable=False)
	status = db.Column(db.String(20), nullable=False, default="active")
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	payment_schedule = db.relationship("PaymentSchedule", backref="booking", uselist=False, cascade="all, delete-orphan")
	payments = db.relationship("Payment", backref="booking", cascade="all, delete-orphan", order_by="Payment.scheduled_date.asc()")

	def __repr__(self) -> str:
		return f"<Booking id={self.id} name={self.customer_name}>"


class PaymentSchedule(db.Model):
	__tablename__ = "payment_schedules"

	id = db.Column(db.Integer, primary_key=True)
	booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False, unique=True)
	upfront_amount_cents = db.Column(db.Integer, nullable=False, default=0)
	recurring_amount_cents = db.Column(db.Integer, nullable=False, default=0)
	frequency = db.Column(db.String(20), nullable=False)
	provider_schedule_id = db.Column(db.String(100), nullable=True)
	next_debit_date = db.Column(db.Date, nullable=True)
	status = db.Column(db.String(20), nullable=False, default="active")
	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	def __repr__(self) -> str:
		return f"<PaymentSchedule booking_id={self.booking_id} frequency={self.frequency}>"


class Payment(db.Model):
	__tablename__ = "payments"

	id = db.Column(db.Integer, primary_key=True)
	booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
	scheduled_date = db.Column(db.Date, nullable=False)
	scheduled_amount_cents = db.Column(db.Integer, nullable=False)

	paid_amount_cents: Optional[int] = db.Column(db.Integer, nullable=True)
	paid_date: Optional[date] = db.Column(db.Date, nullable=True)

	status = db.Column(db.String(20), nullable=False, default="pending")

	provider_payment_id = db.Column(db.String(100), nullable=True)
	invoice_id = db.Column(db.String(100), nullable=True)

	created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	def __repr__(self) -> str:
		return f"<Payment id={self.id} booking_id={self.booking_id} status={self.status}>"