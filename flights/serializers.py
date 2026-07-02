from rest_framework import serializers
from .models import Flight, Booking


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    flight_number = serializers.CharField(source='flight.flight_number', read_only=True)
    origin = serializers.CharField(source='flight.origin', read_only=True)
    destination = serializers.CharField(source='flight.destination', read_only=True)
    passenger_username = serializers.CharField(source='passenger.username', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'pnr', 'status', 'booked_at',
            'passenger', 'passenger_username',
            'flight', 'flight_number', 'origin', 'destination',
        ]
        read_only_fields = ['pnr', 'booked_at', 'passenger']