# Car Rental Payments (Flask)

Implements a workflow: UCollect-hosted payment authority (org-specific URL), Xero invoice creation (OAuth2), UCollect bridge, and reconciliation back to Xero.

## Quickstart

1. Create and edit `.env` or copy `.env.example`:

```
cp .env.example .env
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Run the app:

```
export FLASK_APP=app
flask run --host=0.0.0.0 --port=5000
```

Open `http://localhost:5000` and complete the flow.

## Notes

- UCollect-hosted authority URL: set in `.env` as `UCOLLECT_HOSTED_AUTH_URL=https://...` (org-specific). The booking flow redirects customers there to capture the mandate; UCollect links it to the Xero contact and handles payments for approved invoices.
- Xero requires a one-time OAuth connect at `/xero/connect`. Tokens are persisted and refreshed automatically.
- Uses SQLite by default at `instance/app.db`.

This is a car rental payment module with xero, ucollect and pay advantage.
