# 📈 Stock Insight Platform —  Technical Challenge

A production-ready, Dockerized micro-SaaS platform for stock prediction using LSTM models. It includes a Django REST API, Tailwind-based frontend, and a Telegram bot interface, Stripe gateway etc.


---

## 🔧 Tech Stack

- **Backend**: Django, Django REST Framework
- **Frontend**: Django Templates + Tailwind CSS
- **ML**: LSTM model via Keras/TensorFlow
- **Bot**: python-telegram-bot v22.1
- **Deployment**: Docker + Docker Compose
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Payment**: Stripe (Test Mode)
- **Auth**: JWT (via SimpleJWT)

---

## 🚀 Features

### ✅ Functional

- User registration and login with JWT
- Predict next-day stock price from ticker
- Metrics: MSE, RMSE, R² + two PNG charts
- Web dashboard for viewing and submitting predictions
- Telegram bot interface for quick predictions
- Daily quota system (5/day Free; unlimited for Pro)
- Stripe integration for Pro subscriptions

### ⚙️ Non-Functional

- Docker-based deployment (Gunicorn + healthchecks)
- Static asset handling with WhiteNoise
- .env-based configuration using `python-decouple`

---
### Clone the repository
```bash
git clone https://github.com/Harshiitttt27/stockinsight.git
cd stock-insight
```

### Set Virtual env
```bash
python -m venv env
```

### Configure .env 
```bash
# ───────── Core Django ─────────
DEBUG=False
SECRET_KEY=your-secret-key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1

# ───── Security Hardening ─────
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# ────────── Database ──────────
DATABASE_URL=sqlite:///db.sqlite3

# ───────── JWT Tokens ─────────
JWT_ACCESS_LIFETIME=15
JWT_REFRESH_LIFETIME=1440

# ──────── ML Model ───────────
MODEL_PATH=stock_prediction_model.keras

# ───── Telegram Bot ──────────
BOT_TOKEN=replace-me

# ───────── Stripe Keys ───────
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_PUBLIC_KEY=pk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
```
###🐳 Running the Application
```bash
docker compose up --build
```
Wait for the services to start. Then open:

Web App: http://localhost:8000

Health Check: curl -fs http://localhost:8000/healthz/

## 🤖 Telegram Bot (Dockerized)

The Telegram bot runs automatically as a separate Docker service via:

```yaml
telegrambot:
  build: .
  container_name: telegram_bot
  command: >
    sh -c "sleep 5 && python manage.py telegrambot"
  depends_on:
    - api
  env_file:
    - .env
  volumes:
    - .:/app
```

You **do not need to start it manually**. It's launched automatically when you run:

```bash
docker compose up --build
```

### Available Commands via Telegram:

- `/start` → Link your Telegram account
- `/predict <TICKER>` → Predict next-day price
- `/latest` → Show your most recent prediction
- `/help` → See usage guide
- `/subscribe` (for Stripe upgrade, optional)

### ✅ Notes

- Rate-limited to 10 predictions/minute per user.
- Tracks chat ID via `TelegramUser` model (linked to `auth.User`).
- Structured logging is included for each command.
- Free users: 5 predictions/day  
- Pro users: Unlimited + `/stats` (optional bonus)

### ✅ Bonus: Run predict manually
If you want to rerun prediction after boot:

```bash
docker compose run predict
```

Or from the api container directly:
```bash
docker compose exec api python manage.py predict --all
```


## 💳 Stripe Memberships (Bonus Feature)

Stripe integration enables users to upgrade to a Pro membership for unlimited predictions and access to extra features.

### Plans

| Tier  | Web Features                            | Telegram Features           |
|-------|------------------------------------------|------------------------------|
| Free  | 5 predictions/day, banner shown on UI    | 5 /predict calls/day         |
| Pro   | Unlimited predictions, no ads, priority  | Unlimited /predict + /stats |

### Stripe Flow

- Users can upgrade via the `/subscribe` route.
- Stripe Checkout (Test Mode) processes ₹199/month billing.
- Webhooks handle automatic updates to the user's Pro status.

### Webhook Endpoint

Stripe sends events to:

```
POST /webhooks/stripe/
```

This toggles the `is_pro` flag in `UserProfile` based on subscription status (active, canceled).

### Quota Middleware

- Free users are limited to 5 predictions/day (API and Telegram).
- When exceeded, they receive HTTP 429 or Telegram upgrade prompts.
- Pro users have unlimited access.



### Telegram Upgrade Flow

- When a Free user hits the limit, the bot replies with an upgrade prompt.
- `/subscribe` command triggers Stripe Checkout link.


## 📬 API Collection (Postman)

For testing all API endpoints easily, a Postman collection is provided.

### 📥 Download

👉 [Trading_system.postman_collection.json](Trading_system.postman_collection.json)

### Included Requests

- Register user (`POST /api/v1/register/`)
- Login user (`POST /api/v1/token/`)
- Predict stock price (`POST /api/v1/predict/`)
- Get predictions (`GET /api/v1/predictions/`)
- Health check (`GET /healthz/`)
- Subscribe to Pro (`POST /api/v1/subscribe/`)
- Check Pro status (`GET /api/v1/ispro/`)

> ⚠️ **Note**: Use your own JWT token after login in Postman for protected routes.
> 
### 📬 Contact & Support
If you encounter any issues, bugs, or have questions regarding this project, feel free to reach out:

Email: harrysethi52@gmail.com

🛠 We're here to help. Don't hesitate to reach out!
