from django.db import models
from flights.models import Booking


class SupportTicket(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Resolved', 'Resolved'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='tickets')
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket for {self.booking.pnr}"