from flask import current_app
from ..models import Invoice, Payment, PaymentStatus
from .. import db
from .payadv_service import PayAdvantageClient


class UCollectBridge:
    def __init__(self):
        self.api_key = current_app.config.get("UCOLLECT_API_KEY")
        self.payadv = PayAdvantageClient()

    def sync_and_pay_invoice(self, invoice: Invoice, payadv_token: str) -> Payment:
        payment = Payment(invoice_id=invoice.id, amount_cents=invoice.amount_cents)
        db.session.add(payment)
        db.session.commit()

        # Simulate calling Pay Advantage
        result = self.payadv.charge_with_token(
            token=payadv_token,
            amount_cents=invoice.amount_cents,
            reference=invoice.booking_id,
        )

        payment.payadv_payment_id = result["id"]
        payment.status = PaymentStatus.SUCCESS if result.get("status") == "success" else PaymentStatus.FAILED
        db.session.commit()
        return payment

