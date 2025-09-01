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
- Webhook endpoint: `/webhooks/payadvantage`.

### Xero OAuth Setup
1. Create a Xero app in the Xero Developer portal.
2. Configure the Redirect URI to:
   - `http://localhost:5000/admin/xero/callback`
3. Add scopes:
   - `offline_access accounting.transactions accounting.contacts`
4. Add the following environment variables to your `.env`:
```
XERO_CLIENT_ID=your_xero_client_id
XERO_CLIENT_SECRET=your_xero_client_secret
XERO_REDIRECT_URI=http://localhost:5000/admin/xero/callback
# Optional:
XERO_SCOPES=offline_access accounting.transactions accounting.contacts
XERO_SALES_ACCOUNT_CODE=200
```
5. Start the app and visit `/admin`, then click "Connect Xero".
6. On first connect, we exchange the code for tokens, fetch your tenant id, and store the refresh token so you only authorize once. Tokens are persisted in the database (`xero_auth` table).

### Pay Advantage Setup
You can authenticate with either an API key or with username/password. If you don't have an API key, set username and password.

1. Add to your `.env` (choose ONE auth method):

API key method:
```
PAYADVANTAGE_API_KEY=your_payadvantage_api_key
PAYADVANTAGE_BASE_URL=https://api.test.payadvantage.com.au
PAYADVANTAGE_REDIRECT_URL=http://localhost:5000/admin/bookings
```

Username/password method:
```
PAYADVANTAGE_USERNAME=your_username
PAYADVANTAGE_PASSWORD=your_password
PAYADVANTAGE_BASE_URL=https://api.test.payadvantage.com.au
PAYADVANTAGE_REDIRECT_URL=http://localhost:5000/admin/bookings
```

For production:
```
PAYADVANTAGE_BASE_URL=https://api.payadvantage.com.au
```

Endpoint and payload (v3):
- Direct Debits: POST `/v3/direct_debits`
- Form fields supported:
  - Description (max 50 chars)
  - Upfront Amount (optional)
  - Recurring Amount
  - Recurring Start Date
  - Frequency (weekly, fortnightly, monthly)
  - Reminder Days (0-3)

2. The app will create direct debit schedules against the configured base URL using the chosen authentication.

### Admin
- Admin pages are under `/admin`.
