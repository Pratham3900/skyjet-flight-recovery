from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from flights.models import Booking


@login_required
def passenger_dashboard(request):
    if request.user.is_staff:
        return HttpResponse("Staff accounts use the admin dashboard.")

    bookings = Booking.objects.filter(passenger=request.user).order_by('-booked_at')
    return render(request, 'dashboard/passenger_dashboard.html', {'bookings': bookings})


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return HttpResponse("You are not authorized to access this page.")
    return render(request, 'dashboard/admin_dashboard.html')