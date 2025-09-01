from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import date
from . import db
from .forms import BookingForm
from .models import Booking

main_bp = Blueprint("main", __name__)


def _validate_dates(start_date: date, end_date: date) -> bool:
	return start_date <= end_date


@main_bp.route("/", methods=["GET", "POST"])
def index():
	form = BookingForm()
	if form.validate_on_submit():
		if not _validate_dates(form.start_date.data, form.end_date.data):
			flash("End date must be after start date", "danger")
			return render_template("index.html", form=form)

		booking = Booking(
			customer_name=form.customer_name.data,
			email=form.email.data,
			phone=form.phone.data,
			start_date=form.start_date.data,
			end_date=form.end_date.data,
			status="active",
		)
		db.session.add(booking)
		db.session.commit()
		return redirect(url_for("main.success", booking_id=booking.id))

	return render_template("index.html", form=form)


@main_bp.route("/success/<int:booking_id>")
def success(booking_id: int):
	booking = Booking.query.get_or_404(booking_id)
	return render_template("success.html", booking=booking)