# SkyJet Airways — Self-Service Flight Recovery MVP

22North Product Engineering Challenge 2026 — Challenge 1

## Setup

1. Clone the repo
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and fill in your Gmail app password
6. Run migrations: `python manage.py migrate`
7. Seed demo flights: `python manage.py seed_flights`
8. Create admin: `python manage.py createsuperuser`
9. Run server: `python manage.py runserver`

## Apps
- `accounts` — registration, login, welcome email
- `flights` — flight browsing, booking, booking confirmation email, DRF API
- `recovery` — disruption engine, recovery portal (rebook/refund/voucher/agent)
- `dashboard` — passenger and admin dashboards