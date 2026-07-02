from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db.models import Q
from itertools import groupby

from flights.models import Flight, Booking
from .models import SupportTicket
from .forms import FlightStatusForm, RecoveryActionForm
from .utils import send_disruption_emails, send_recovery_confirmation_email, DELAY_THRESHOLD_MINUTES



# --------------------------------
# ADMIN: manage flight status (triggers disruption engine)
# --------------------------------
@login_required
def admin_flight_list(request):
    if not request.user.is_staff:
        return HttpResponse("You are not authorized to access this page.")

    query = request.GET.get('q', '').strip()

    flights = Flight.objects.all().order_by('origin', 'destination', 'departure_time')

    if query:
        flights = flights.filter(
            Q(origin__icontains=query) |
            Q(destination__icontains=query) |
            Q(flight_number__icontains=query) |
            Q(status__icontains=query)
        )

    # Group consecutive flights by (origin, destination) route
    grouped_routes = []
    for (origin, destination), group in groupby(flights, key=lambda f: (f.origin, f.destination)):
        grouped_routes.append({
            'origin': origin,
            'destination': destination,
            'flights': list(group),
        })

    return render(request, 'recovery/admin_flight_list.html', {
        'grouped_routes': grouped_routes,
        'query': query,
    })


@login_required
def admin_update_flight_status(request, flight_id):
    if not request.user.is_staff:
        return HttpResponse("You are not authorized to access this page.")

    flight = get_object_or_404(Flight, id=flight_id)

    if request.method == 'POST':
        form = FlightStatusForm(request.POST, instance=flight)
        if form.is_valid():
            updated_flight = form.save()

            if updated_flight.status in ['Delayed', 'Cancelled']:
                send_disruption_emails(updated_flight, request)   # ← pass request now

            return redirect('admin_flight_list')
    else:
        form = FlightStatusForm(instance=flight)

    return render(request, 'recovery/admin_flight_status.html', {'form': form, 'flight': flight})

# --------------------------------
# PASSENGER: recovery portal (public via PNR — no login required)
# --------------------------------
def recovery_portal(request, pnr):
    booking = get_object_or_404(Booking, pnr=pnr)
    flight = booking.flight

    eligible = flight.status == 'Cancelled' or (
        flight.status == 'Delayed' and flight.delay_minutes >= DELAY_THRESHOLD_MINUTES
    )

    if not eligible:
        return render(request, 'recovery/portal.html', {
            'booking': booking, 'flight': flight, 'eligible': False
        })

    if request.method == 'POST':
        form = RecoveryActionForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            if action == 'rebook':
                return redirect('recovery_rebook_select', pnr=pnr)
            elif action == 'refund':
                return redirect('recovery_refund', pnr=pnr)
            elif action == 'voucher':
                return redirect('recovery_voucher', pnr=pnr)
          
    else:
        form = RecoveryActionForm()

    return render(request, 'recovery/portal.html', {
        'booking': booking, 'flight': flight, 'eligible': True, 'form': form
    })


def recovery_rebook_select(request, pnr):
    booking = get_object_or_404(Booking, pnr=pnr)
    alt_flights = Flight.objects.filter(
        origin=booking.flight.origin,
        destination=booking.flight.destination,
        status='Scheduled'
    ).exclude(id=booking.flight.id)

    if request.method == 'POST':
        new_flight_id = request.POST.get('flight_id')
        new_flight = get_object_or_404(Flight, id=new_flight_id)

        booking.status = 'Rebooked'
        booking.save()

        new_booking = Booking.objects.create(passenger=booking.passenger, flight=new_flight)

        send_recovery_confirmation_email(
            new_booking, 'Rebooked',
            detail=f"New flight {new_flight.flight_number} on {new_flight.departure_time}"
        )
        return redirect('recovery_done', pnr=new_booking.pnr)

    return render(request, 'recovery/rebook_select.html', {'booking': booking, 'alt_flights': alt_flights})


def recovery_refund(request, pnr):
    booking = get_object_or_404(Booking, pnr=pnr)
    booking.status = 'Refunded'
    booking.save()
    send_recovery_confirmation_email(booking, 'Refund initiated')
    return redirect('recovery_done', pnr=pnr)


def recovery_voucher(request, pnr):
    booking = get_object_or_404(Booking, pnr=pnr)
    booking.status = 'Voucher Issued'
    booking.save()
    send_recovery_confirmation_email(booking, 'Travel voucher issued')
    return redirect('recovery_done', pnr=pnr)


def recovery_done(request, pnr):
    booking = get_object_or_404(Booking, pnr=pnr)
    return render(request, 'recovery/action_done.html', {'booking': booking})

@login_required
def admin_bookings_list(request):
    if not request.user.is_staff:
        return HttpResponse("You are not authorized to access this page.")

    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    bookings = Booking.objects.select_related('flight', 'passenger').order_by('-booked_at')

    if query:
        bookings = bookings.filter(
            Q(pnr__icontains=query) |
            Q(passenger__username__icontains=query) |
            Q(flight__flight_number__icontains=query)
        )

    if status_filter:
        bookings = bookings.filter(status=status_filter)

    open_tickets = SupportTicket.objects.filter(status='Open').select_related('booking').count()

    return render(request, 'recovery/admin_bookings_list.html', {
        'bookings': bookings,
        'query': query,
        'status_filter': status_filter,
        'status_choices': Booking.STATUS_CHOICES,
        'open_tickets': open_tickets,
    })
