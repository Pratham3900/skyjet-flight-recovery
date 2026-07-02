import uuid
from django.db import models
from django.contrib.auth.models import User


class Flight(models.Model):
    STATUS_CHOICES = [
        ('Scheduled', 'Scheduled'),
        ('Delayed', 'Delayed'),
        ('Cancelled', 'Cancelled'),
    ]

    flight_number = models.CharField(max_length=10, unique=True)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Scheduled')
    delay_minutes = models.IntegerField(default=0)
    seats_available = models.IntegerField(default=50)

    def __str__(self):
        return f"{self.flight_number} ({self.origin} → {self.destination})"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled'),
        ('Rebooked', 'Rebooked'),
        ('Refunded', 'Refunded'),
         ('Voucher Issued', 'Voucher Issued'),
        ('Escalated', 'Escalated'),
    ]

    pnr = models.CharField(max_length=8, unique=True, editable=False)
    passenger = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Confirmed')
    booked_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pnr:
            self.pnr = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pnr} - {self.passenger.username}"