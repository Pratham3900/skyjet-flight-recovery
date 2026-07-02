from django.urls import path
from . import views

urlpatterns = [
    # Admin
    path('admin/flights/', views.admin_flight_list, name='admin_flight_list'),
    path('admin/flights/<int:flight_id>/status/', views.admin_update_flight_status, name='admin_update_flight_status'),
     path('admin/bookings/', views.admin_bookings_list, name='admin_bookings_list'),   # NEW


    # Passenger recovery portal (public, PNR-based)
    path('portal/<str:pnr>/', views.recovery_portal, name='recovery_portal'),
    path('portal/<str:pnr>/rebook/', views.recovery_rebook_select, name='recovery_rebook_select'),
    path('portal/<str:pnr>/refund/', views.recovery_refund, name='recovery_refund'),
    path('portal/<str:pnr>/voucher/', views.recovery_voucher, name='recovery_voucher'),
    path('portal/<str:pnr>/done/', views.recovery_done, name='recovery_done'),
]
