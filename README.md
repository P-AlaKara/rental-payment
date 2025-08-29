# Car Rental Payments (Flask)

Implements a workflow: Pay Advantage hosted payment authority (Basic Auth with API username/password), Xero invoice creation (OAuth2), UCollect bridge, and reconciliation back to Xero.

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

- Pay Advantage uses Basic Auth. Set in `.env`:
  - `PAYADV_USERNAME=your-api-username`
  - `PAYADV_PASSWORD=your-api-password`
  - Optionally edit `PAYADV_BASE_URL` and `PAYADV_HOSTED_URL` if your environment differs.
- Xero requires a one-time OAuth connect at `/xero/connect`. Tokens are persisted and refreshed automatically.
- Replace service clients in `app/services/*.py` with your production endpoints when ready.
- Uses SQLite by default at `instance/app.db`.

This is a car rental payment module with xero, ucollect and pay advantage.
