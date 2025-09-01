## Car Rental Booking - Flask App

### Setup

1. Create and activate a virtual environment
```bash
python3 -m venv .venv && source .venv/bin/activate
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Configure environment (optional)
Create a `.env` file in the project root:
```bash
FLASK_ENV=development
SECRET_KEY=dev-secret
DATABASE_URL=sqlite:////workspace/app.db
```

4. Run the app
```bash
python run.py
```

### Integrations
- Pay Advantage and Xero clients are stub-friendly. Replace with real API keys and endpoints in `app/pay_advantage.py` and `app/xero_client.py`.
- Webhook endpoint: `/webhooks/payadvantage`.

### Admin
- Admin pages are under `/admin`.
