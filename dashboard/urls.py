from django.urls import path
from . import views

urlpatterns = [
    path('', views.passenger_dashboard, name='passenger_dashboard'),
    path('admin/', views.admin_dashboard, name='admin_dashboard'),
]