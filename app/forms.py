from flask_wtf import FlaskForm
from wtforms import StringField, DateField, DecimalField, SelectField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Email, Length, NumberRange


class BookingForm(FlaskForm):
	customer_name = StringField("Full Name", validators=[DataRequired(), Length(max=120)])
	email = StringField("Email", validators=[DataRequired(), Email(), Length(max=200)])
	phone = StringField("Phone", validators=[DataRequired(), Length(max=50)])
	start_date = DateField("Start Date", validators=[DataRequired()])
	end_date = DateField("End Date", validators=[DataRequired()])
	submit = SubmitField("Book Now")


class PaymentScheduleForm(FlaskForm):
	upfront_amount = DecimalField("Upfront Amount (in your currency)", places=2, validators=[DataRequired(), NumberRange(min=0)])
	recurring_amount = DecimalField("Recurring Amount", places=2, validators=[DataRequired(), NumberRange(min=0)])
	frequency = SelectField(
		"Frequency",
		choices=[("weekly", "Weekly"), ("fortnightly", "Fortnightly"), ("monthly", "Monthly")],
		validators=[DataRequired()],
	)
	recurring_date_start = DateField("Recurring Start Date", validators=[DataRequired()])
	description = StringField("Payment Description", validators=[DataRequired(), Length(max=50)])
	reminder_days = IntegerField("Reminder Days (0-3)", validators=[DataRequired(), NumberRange(min=0, max=3)])
	submit = SubmitField("Set Direct Debit")