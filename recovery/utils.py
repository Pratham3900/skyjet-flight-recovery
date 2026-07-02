from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

DELAY_THRESHOLD_MINUTES = 120


def send_disruption_emails(flight, request):
    """
    Called when admin changes flight status.
    request is required to build an absolute portal URL for the email.
    """
    bookings = flight.booking_set.filter(status='Confirmed')

    for booking in bookings:
        show_portal = flight.status == 'Cancelled' or (
            flight.status == 'Delayed' and flight.delay_minutes >= DELAY_THRESHOLD_MINUTES
        )

        portal_url = None
        if show_portal:
            portal_url = request.build_absolute_uri(f"/recovery/portal/{booking.pnr}/")

        html_content = render_to_string('recovery/emails/disruption_email.html', {
            'username': booking.passenger.username,
            'flight': flight,
            'pnr': booking.pnr,
            'portal_url': portal_url,
            'show_portal': show_portal,
        })

        email = EmailMultiAlternatives(
            subject=f"Update on your flight {flight.flight_number}",
            body=f"Your flight {flight.flight_number} status: {flight.status}.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.passenger.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)


def send_recovery_confirmation_email(booking, action_label, detail=""):
    # unchanged
    html_content = render_to_string('recovery/emails/recovery_confirmation_email.html', {
        'username': booking.passenger.username,
        'pnr': booking.pnr,
        'action_label': action_label,
        'detail': detail,
        'flight': booking.flight,
    })

    email = EmailMultiAlternatives(
        subject=f"Your recovery request is confirmed — {booking.pnr}",
        body=f"Your booking {booking.pnr} has been updated: {action_label}.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[booking.passenger.email],
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)