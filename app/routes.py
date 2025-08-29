from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash
from . import db
from .models import Customer, Invoice, InvoiceStatus, PaymentStatus
from .services.payadv_service import PayAdvantageClient
from .services.xero_service import XeroClient
from .services.ucollect_service import UCollectBridge


bp = Blueprint("main", __name__)


@bp.get("/")
def index():
    return render_template("index.html")


@bp.post("/start")
def start_booking():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip()
    booking_id = request.form.get("booking_id", "").strip()
    amount = float(request.form.get("amount", 0))
    amount_cents = int(round(amount * 100))

    if not (name and email and booking_id and amount_cents > 0):
        flash("All fields are required and amount must be positive.")
        return redirect(url_for("main.index"))

    customer = Customer.query.filter_by(email=email).first()
    if not customer:
        customer = Customer(name=name, email=email)
        db.session.add(customer)
        db.session.commit()

    invoice = Invoice(
        booking_id=booking_id,
        amount_cents=amount_cents,
        customer_id=customer.id,
        status=InvoiceStatus.DRAFT,
    )
    db.session.add(invoice)
    db.session.commit()

    # Create hosted payment authority session
    payadv = PayAdvantageClient()
    redirect_url = url_for("main.hosted_callback", _external=True)
    session = payadv.create_customer_and_authority(name=name, email=email, redirect_url=redirect_url)

    # Store token temporarily when callback returns
    current_app.logger.info("Hosted session created: %s", session)
    return redirect(session["hosted_url"])


@bp.get("/hosted")
def hosted_page():
    # Simulated hosted page; in production this is on Pay Advantage domain
    token = request.args.get("token")
    name = request.args.get("name")
    email = request.args.get("email")
    redirect_url = request.args.get("redirect")
    return render_template("hosted_payment.html", token=token, name=name, email=email, redirect_url=redirect_url)


@bp.post("/hosted/callback")
def hosted_callback():
    token = request.form.get("token")
    email = request.form.get("email")

    customer = Customer.query.filter_by(email=email).first()
    if not customer:
        flash("Customer not found for callback")
        return redirect(url_for("main.index"))

    customer.payadv_customer_id = customer.payadv_customer_id or f"cust_{customer.id}"
    customer.payadv_token = token
    db.session.commit()

    # Create and approve an invoice in Xero, then simulate UCollect sync and payment
    invoice = Invoice.query.filter_by(customer_id=customer.id).order_by(Invoice.id.desc()).first()
    xero = XeroClient()
    xero_inv = xero.create_and_approve_invoice(contact_name=customer.name, contact_email=customer.email, amount_cents=invoice.amount_cents, reference=invoice.booking_id)
    invoice.xero_invoice_id = xero_inv["id"]
    invoice.status = InvoiceStatus.APPROVED
    db.session.commit()

    ucollect = UCollectBridge()
    payment = ucollect.sync_and_pay_invoice(invoice=invoice, payadv_token=customer.payadv_token)

    if payment.status == PaymentStatus.SUCCESS:
        invoice.status = InvoiceStatus.PAID
        db.session.commit()
        flash("Payment successful and invoice marked as PAID")
    else:
        flash("Payment failed. Please try again or use another method.")

    return redirect(url_for("main.invoice_view", invoice_id=invoice.id))


@bp.get("/invoice/<int:invoice_id>")
def invoice_view(invoice_id: int):
    invoice = Invoice.query.get_or_404(invoice_id)
    customer = Customer.query.get(invoice.customer_id)
    return render_template("invoice.html", invoice=invoice, customer=customer)


@bp.get("/admin")
def admin():
    customers = Customer.query.all()
    return render_template("admin.html", customers=customers)

