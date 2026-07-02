from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.http import HttpResponse

from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Flight, Booking
from .forms import BookingConfirmForm
from .serializers import FlightSerializer, BookingSerializer


# --------------------------------
# EXISTING DJANGO VIEWS (unchanged)
# --------------------------------
@login_required
def flight_list(request):
    if request.user.is_staff:
        return HttpResponse("Staff accounts do not book flights.")
    flights = Flight.objects.filter(status='Scheduled').order_by('departure_time')
    return render(request, 'flights/flight_list.html', {'flights': flights})


@login_required
def book_flight(request, flight_id):
    if request.user.is_staff:
        return HttpResponse("Staff accounts do not book flights.")
    flight = get_object_or_404(Flight, id=flight_id)
    if request.method == 'POST':
        form = BookingConfirmForm(request.POST)
        if form.is_valid():
            booking = Booking.objects.create(passenger=request.user, flight=flight)

            try:
                html_content = render_to_string('flights/emails/booking_email.html', {
                    'username': request.user.username,
                    'pnr': booking.pnr,
                    'flight': flight,
                })
                email = EmailMultiAlternatives(
                    subject=f'Booking Confirmed — PNR {booking.pnr}',
                    body=f"Your booking for flight {flight.flight_number} is confirmed. PNR: {booking.pnr}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[request.user.email],
                )
                email.attach_alternative(html_content, "text/html")
                email.send(fail_silently=False)
            except Exception as e:
                pass  # booking still succeeds even if email fails

            return redirect('booking_confirmation', booking_id=booking.id)
    return redirect('flight_list')


@login_required
def booking_confirmation(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, passenger=request.user)
    return render(request, 'flights/booking_confirmation.html', {'booking': booking})


# --------------------------------
# DRF API VIEWS FOR FLIGHT
# --------------------------------
class FlightListAPIView(generics.ListAPIView):
    """GET /api/flights/  — list all flights (optionally filter by status)"""
    serializer_class = FlightSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Flight.objects.all().order_by('departure_time')
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset


class FlightRetrieveAPIView(generics.RetrieveAPIView):
    """GET /api/flights/<id>/ — single flight detail"""
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [permissions.IsAuthenticated]


class FlightStatusUpdateAPIView(generics.UpdateAPIView):
    """PATCH /api/flights/<id>/status/ — admin updates status (used in Part 3)"""
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [permissions.IsAdminUser]


# --------------------------------
# DRF API VIEWS FOR BOOKING
# --------------------------------
class BookingListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/bookings/  — passenger sees only their own bookings
    POST /api/bookings/  — create a booking (used by mobile app / partner integration)
    """
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all().order_by('-booked_at')
        return Booking.objects.filter(passenger=self.request.user).order_by('-booked_at')

    def perform_create(self, serializer):
        serializer.save(passenger=self.request.user)


class BookingRetrieveAPIView(generics.RetrieveAPIView):
    """GET /api/bookings/<id>/ — booking detail (own bookings only, unless staff)"""
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Booking.objects.all()
        return Booking.objects.filter(passenger=self.request.user)


class BookingByPNRAPIView(APIView):
    """
    GET /api/bookings/pnr/<pnr>/
    Lookup a booking by PNR — this is the endpoint the recovery portal
    will use in Part 3 so a passenger can check status without logging in
    via the notification email link.
    """
    permission_classes = [permissions.AllowAny]

    def get(self, request, pnr):
        booking = get_object_or_404(Booking, pnr=pnr)
        serializer = BookingSerializer(booking)
        return Response(serializer.data)