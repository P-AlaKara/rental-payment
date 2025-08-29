# Car Rental Payments (Flask)

Implements a simulated workflow: Pay Advantage hosted payment authority, Xero invoice creation, UCollect bridge, and reconciliation back to Xero.

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

- This project mocks external APIs for Pay Advantage, Xero, and UCollect.
- Replace service clients in `app/services/*.py` to integrate real APIs.
- Uses SQLite by default at `instance/app.db`.

This is a car rental payment module with xero, ucollect and pay advantage.
