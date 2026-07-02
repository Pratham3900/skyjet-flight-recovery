from django.urls import path
from .views import (
    flight_list,
    book_flight,
    booking_confirmation,
    FlightListAPIView,
    FlightRetrieveAPIView,
    FlightStatusUpdateAPIView,
    BookingListCreateAPIView,
    BookingRetrieveAPIView,
    BookingByPNRAPIView,
)

urlpatterns = [
    # Django views (passenger-facing pages)
    path('', flight_list, name='flight_list'),
    path('book/<int:flight_id>/', book_flight, name='book_flight'),
    path('confirmation/<int:booking_id>/', booking_confirmation, name='booking_confirmation'),

    # DRF API — Flights
    path('api/flights/', FlightListAPIView.as_view(), name='flight_list_api'),
    path('api/flights/<int:pk>/', FlightRetrieveAPIView.as_view(), name='flight_detail_api'),
    path('api/flights/<int:pk>/status/', FlightStatusUpdateAPIView.as_view(), name='flight_status_update_api'),

    # DRF API — Bookings
    path('api/bookings/', BookingListCreateAPIView.as_view(), name='booking_list_create_api'),
    path('api/bookings/<int:pk>/', BookingRetrieveAPIView.as_view(), name='booking_detail_api'),
    path('api/bookings/pnr/<str:pnr>/', BookingByPNRAPIView.as_view(), name='booking_by_pnr_api'),
]