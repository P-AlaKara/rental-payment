from flask import Blueprint, render_template, request, redirect, url_for, current_app, flash, session
from . import db
from .models import Customer, Invoice, InvoiceStatus, PaymentStatus
from .services.payadv_service import PayAdvantageClient
from .services.xero_service import XeroClient
from .services.ucollect_service import UCollectBridge
from authlib.integrations.flask_client import OAuth


bp = Blueprint("main", __name__)
oauth = OAuth()


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
    hosted = payadv.create_customer_and_authority(name=name, email=email, redirect_url=redirect_url)

    # Store token temporarily when callback returns
    current_app.logger.info("Hosted session created: %s", hosted)
    return redirect(hosted["hosted_url"])


@bp.get("/hosted")
def hosted_page():
    # Simulated hosted page; in production this is on Pay Advantage domain
    token = request.args.get("token")
    name = request.args.get("name")
    email = request.args.get("email")
    redirect_url = request.args.get("redirect")
    return render_template("hosted_payment.html", token=token, name=name, email=email, redirect_url=redirect_url)


@bp.route("/hosted/callback", methods=["GET", "POST"])
def hosted_callback():
    token = request.values.get("token")
    email = request.values.get("email")

    customer = Customer.query.filter_by(email=email).first()
    if not customer:
        flash("Customer not found for callback")
        return redirect(url_for("main.index"))

    customer.payadv_customer_id = customer.payadv_customer_id or f"cust_{customer.id}"
    customer.payadv_token = token
    db.session.commit()

    # Create and approve an invoice in Xero, then simulate UCollect sync and payment
    invoice = Invoice.query.filter_by(customer_id=customer.id).order_by(Invoice.id.desc()).first()
    # Ensure we have Xero OAuth access token
    access_token = session.get("xero_access_token")
    if not access_token:
        flash("Connect to Xero first.")
        return redirect(url_for("main.xero_connect"))

    xero = XeroClient()
    xero_inv = xero.create_and_approve_invoice(
        contact_name=customer.name,
        contact_email=customer.email,
        amount_cents=invoice.amount_cents,
        reference=invoice.booking_id,
        access_token=access_token,
    )
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


# --- Xero OAuth ---
@bp.before_app_first_request
def init_oauth():
    oauth.init_app(current_app)
    oauth.register(
        name="xero",
        client_id=current_app.config["XERO_CLIENT_ID"],
        client_secret=current_app.config["XERO_CLIENT_SECRET"],
        api_base_url="https://api.xero.com/",
        access_token_url="https://identity.xero.com/connect/token",
        authorize_url="https://login.xero.com/identity/connect/authorize",
        client_kwargs={
            "scope": current_app.config["XERO_SCOPES"],
        },
    )


@bp.get("/xero/connect")
def xero_connect():
    redirect_uri = current_app.config["XERO_REDIRECT_URI"]
    return oauth.xero.authorize_redirect(redirect_uri)


@bp.get("/xero/callback")
def xero_callback():
    token = oauth.xero.authorize_access_token()
    # Persist minimal tokens in session (for demo). For production, persist in DB with refresh.
    session["xero_access_token"] = token.get("access_token")
    session["xero_refresh_token"] = token.get("refresh_token")
    flash("Connected to Xero.")
    return redirect(url_for("main.index"))

