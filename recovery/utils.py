from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

DELAY_THRESHOLD_MINUTES = 120


def send_disruption_emails(flight, request):
    bookings = flight.booking_set.filter(status='Confirmed')

    for booking in bookings:
        show_portal = flight.status == 'Cancelled' or (
            flight.status == 'Delayed' and flight.delay_minutes >= DELAY_THRESHOLD_MINUTES
        )

        if show_portal:
            booking.status = 'Disrupted'
            booking.save()

        portal_url = None
        if show_portal:
            portal_url = request.build_absolute_uri(f"/recovery/portal/{booking.pnr}/")

        try:
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
        except Exception as e:
            print(f"Disruption email failed for {booking.pnr}: {e}")


def send_recovery_confirmation_email(booking, action_label, detail=""):
    try:
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
    except Exception as e:
        print(f"Recovery confirmation email failed for {booking.pnr}: {e}")