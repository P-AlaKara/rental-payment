from flask import Blueprint, request, jsonify
from datetime import date
from . import db
from .models import Payment

webhooks_bp = Blueprint("webhooks", __name__)


@webhooks_bp.route("/payadvantage", methods=["POST"])
def payadvantage_webhook():
	payload = request.get_json(silent=True) or {}
	provider_payment_id = payload.get("payment_id")
	status = payload.get("status")  # expected: pending, complete, overdue
	paid_amount_cents = payload.get("paid_amount_cents")
	paid_date_str = payload.get("paid_date")  # YYYY-MM-DD

	if not provider_payment_id:
		return jsonify({"error": "missing payment_id"}), 400

	payment = Payment.query.filter_by(provider_payment_id=provider_payment_id).first()
	if not payment:
		return jsonify({"error": "payment not found"}), 404

	if status:
		payment.status = status
	if paid_amount_cents is not None:
		payment.paid_amount_cents = int(paid_amount_cents)
	if paid_date_str:
		try:
			payment.paid_date = date.fromisoformat(paid_date_str)
		except ValueError:
			pass

	db.session.commit()
	return jsonify({"ok": True})