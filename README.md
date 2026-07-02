# SkyJet Airways — Self-Service Flight Recovery MVP

**22North Product Engineering Challenge 2026 — Challenge 1: Self-Service Flight Recovery**

A digital self-service platform that lets passengers resolve flight disruptions — cancellations and major delays — without calling a contact center agent. Built as a 48-hour MVP for a regional airline operating 65 aircraft across Asia.

**Live demo:** [https://skyjet-flight-recovery.onrender.com](https://skyjet-flight-recovery.onrender.com)

**Demo video / screen recording:** https://drive.google.com/drive/folders/1ZuWH_fI-7wzH_1EV24kicvsEZbwC1GuT?usp=sharing

**GitHub repo:** [https://github.com/Pratham3900/skyjet-flight-recovery](https://github.com/Pratham3900/skyjet-flight-recovery)

## API documentation (Swagger)

Interactive API documentation is available at:

**[https://skyjet-flight-recovery.onrender.com/api/docs/](https://skyjet-flight-recovery.onrender.com/api/docs/)**

Generated automatically from the Django REST Framework views using `drf-spectacular` (OpenAPI 3 schema).

> Note: the live app is hosted on Render's free tier, which spins down after 15 minutes of inactivity. The first request after idle may take 30–50 seconds to respond.

---

## Problem statement

During weather disruptions, nearly 40% of SkyJet's passengers call the contact center to ask whether their flight is cancelled, whether they can move to another flight, or whether they're eligible for a refund — with average wait times exceeding 25 minutes. This MVP gives passengers a way to resolve all three questions themselves, instantly, through a link sent straight to their inbox.

---

## End-to-end user flow

This is the exact flow implemented in the app, from registration through disruption recovery:

1. **Passenger registers** on the web app (username, email, password)
2. **Welcome email** is sent immediately to their inbox, confirming account creation
3. Passenger logs in and lands on their **dashboard**
4. Passenger **books a flight** from the available flight list
5. **Booking confirmation email** is sent with PNR, flight number, route, and departure/arrival times
6. Passenger can see all their bookings and live statuses on their **dashboard**
7. **Admin** (Django superuser) manages flights from an internal ops panel and can change a flight's status to **Scheduled**, **Delayed** (with a delay duration in minutes), or **Cancelled**
8. When a flight is marked disrupted, the system checks the disruption type:
   - **Cancelled** → every affected passenger is notified with recovery options
   - **Delayed, and delay ≥ 120 minutes** → passenger is notified with recovery options
   - **Delayed, and delay < 120 minutes** → passenger receives **no email and no portal access** — the disruption is considered minor enough not to need self-service action, avoiding notification fatigue for short delays
9. Affected passengers eligible for recovery receive a **disruption email** with a **PNR-based recovery portal link** — this link works without logging in, since it's meant to be opened directly from the email on any device
10. On the **recovery portal**, the passenger picks one of three options:
    - **Rebook** — choose an alternate flight on the same route, instantly re-booked
    - **Refund** — booking marked refunded (no live payment processing, per constraint)
    - **Travel voucher** — booking marked as voucher issued
11. Whichever option is chosen, a **recovery confirmation email** is sent, and the passenger's dashboard status updates in real time (Confirm → Rebooked / Refunded / Voucher Issued)
12. Admin can view **all bookings** across the airline in one place — searchable and filterable by status — to monitor how many passengers self-resolved 

---

## Features

- Passenger registration, login, and dashboard (Django auth)
- Styled HTML transactional emails: welcome, booking confirmation, disruption notice, recovery confirmation
- Admin flight management: update status, set delay duration, trigger disruption engine
- Route-grouped, searchable admin flight list (grouped by origin → destination)
- Rule-based disruption eligibility (cancellation vs. delay threshold)
- Public, PNR-based recovery portal — no login required, matches how a real airline disruption email link would work
- three recovery actions: Rebook, Refund, Travel voucher
- Admin bookings dashboard with search + status filter, and an open-ticket counter
- REST API layer (Django REST Framework) for flights and bookings, including a public PNR lookup endpoint
- Seed script generating a realistic 65-aircraft flight schedule across Asian routes, with time-of-day flight patterns (morning/afternoon/evening/night) instead of fully random timings

---

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Django 5.2, Python 3.11 |
| API | Django REST Framework |
| Database | SQLite (local dev) / PostgreSQL (production, Render) |
| Email | Django SMTP backend via Gmail (HTML transactional emails) |
| Deployment | Render (Web Service + PostgreSQL) |
| Frontend | Django templates,CSS (no framework) |

---

## Project structure

```
skyjet_recovery/
├── core/          # Home page
├── accounts/      # Register, login, logout, welcome email
├── flights/       # Flight model, booking, booking confirmation email, DRF API
├── recovery/      # Disruption engine, recovery portal, support tickets
├── dashboard/     # Passenger dashboard, admin dashboard
├── templates/      # Shared base template
├── static/css/     # Site-wide styling
└── skyjet_recovery/  # Project settings, urls
```

---

## API design

| Method | Endpoint | Purpose | Auth |
|---|---|---|---|
| `POST` | `/accounts/register/` | Register a new passenger | Public |
| `POST` | `/accounts/login/` | Login | Public |
| `GET` | `/flights/api/flights/` | List flights (optional `?status=` filter) | Authenticated |
| `GET` | `/flights/api/flights/<id>/` | Flight detail | Authenticated |
| `PATCH` | `/flights/api/flights/<id>/status/` | Admin updates flight status (Delayed/Cancelled), triggers disruption engine | Staff only |
| `GET` | `/flights/api/bookings/` | List own bookings (all bookings if staff) | Authenticated |
| `POST` | `/flights/api/bookings/` | Create a booking | Authenticated |
| `GET` | `/flights/api/bookings/<id>/` | Booking detail | Owner or staff |
| `GET` | `/flights/api/bookings/pnr/<pnr>/` | Look up a booking by PNR — no login required | Public |
| `GET` | `/recovery/portal/<pnr>/` | Recovery portal for a disrupted booking | Public (PNR-based) |
| `POST` | `/recovery/portal/<pnr>/rebook\|refund\|voucher\|agent/` | Execute a recovery action | Public (PNR-based) |

Built with Django REST Framework's class-based generic views (`ListAPIView`, `ListCreateAPIView`, `RetrieveAPIView`, `UpdateAPIView`) and a custom `APIView` for the public PNR lookup.

---

## Key assumptions

- No payment gateway — Refund and Voucher just update booking status
- Flight and passenger data is mock/seeded, not a real airline inventory system
- Delay < 120 minutes = notify only; ≥ 120 minutes or Cancelled = recovery options offered
- Email is the only notification channel (no SMS/push)
- SQLite for local dev, PostgreSQL in production
- Admin access uses Django's built-in is_staff flag
- Recovery portal is public and PNR-based, so passengers can act from the email link without logging in

---
## Demo credentials

**Admin (staff) login** — pre-created via environment variables at deploy time, since Render's free tier does not provide shell access to run `createsuperuser` manually:
```
Username: admin
Password: 12345678
```

**Passenger login** — no fixed demo account. Register a new passenger account directly on the live app (`/accounts/register/`) using any email you can access, since the flow depends on receiving real welcome/booking/recovery emails.

## Known limitations

- Email does not work on the live Render deployment. Render's free hosting blocks outgoing email connections (SMTP) as a spam-prevention measure — this is a hosting platform restriction, not a bug in the app. Email works correctly when the app is run locally. All other actions (registration, booking, admin flight updates, recovery options) complete successfully on Render regardless.
  
## Future enhancements

- Move email sending to a transactional email API to work reliably on any host
- SMS/push notifications alongside email
- Real payment gateway integration for refunds
- Role-based admin permissions beyond a single `is_staff` flag
- Background job queue (e.g. Celery) for async email sending instead of blocking the request

## Setup instructions (run locally)

**1. Clone the repository**
```bash
git clone https://github.com/Pratham3900/skyjet-flight-recovery.git
cd skyjet-flight-recovery
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

Copy `.env.example` to a new file named `.env`, then fill in your own Gmail credentials:
```
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-gmail-app-password
```

To generate a Gmail app password: enable 2-Step Verification on your Google account, then go to **Google Account → Security → App passwords**, generate one for "Mail", and paste the 16-character code above (no spaces).

**5. Run migrations**
```bash
python manage.py migrate
```

**6. Create an admin (superuser) account**
```bash
python manage.py createsuperuser
```

**7. Seed demo flight data (Test Data Must run for See the flight data)**
```bash
python manage.py seed_flights
```
This generates flights across a 65-aircraft Asia network with realistic morning/afternoon/evening/night scheduling patterns.

**8. Run the development server**
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser.

---

## Demo walkthrough (for evaluators)

1. Register a new passenger account with a real, checkable email address
2. Check inbox for the welcome email
3. Log in, book any available flight, check inbox for the booking confirmation email
4. Log out, log back in as the superuser account created in setup step 6
5. Go to **Dashboard → Manage flights**, find the flight you just booked, and mark it **Cancelled** (or **Delayed** with delay minutes ≥ 120)
6. Check the passenger's inbox for the disruption email with the recovery portal link
7. Open that link (no login needed) and pick a recovery option — Rebook, Refund, Voucher
8. Check inbox again for the recovery confirmation email
9. Log in as the passenger and confirm the dashboard now reflects the updated booking status
10. Log in as admin again and check **Dashboard → View bookings** to see the resolved booking
---

## Screenshots and demo assets

- Full screen recording / walkthrough video: https://drive.google.com/drive/folders/1ZuWH_fI-7wzH_1EV24kicvsEZbwC1GuT?usp=sharing
- Screenshots: https://drive.google.com/drive/folders/1ZuWH_fI-7wzH_1EV24kicvsEZbwC1GuT?usp=sharing

---

## Acknowledgment

Help during project: Claude (AI) and Django REST Framework.
---

## Author

Pratham Danawala — MCA, CHARUSAT University (CMPICA)
StudentID- 25MCA046
