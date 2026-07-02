from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from flights.models import Flight


ASIA_ROUTES = [
    ('Mumbai', 'Delhi'), ('Delhi', 'Bengaluru'), ('Ahmedabad', 'Mumbai'),
    ('Bengaluru', 'Chennai'), ('Delhi', 'Kolkata'), ('Mumbai', 'Singapore'),
    ('Delhi', 'Dubai'), ('Bengaluru', 'Bangkok'), ('Mumbai', 'Colombo'),
    ('Delhi', 'Kathmandu'), ('Chennai', 'Singapore'), ('Kolkata', 'Bangkok'),
    ('Ahmedabad', 'Dubai'), ('Delhi', 'Male'), ('Mumbai', 'Doha'),
]

# Hour ranges (24-hr clock) for each time-of-day band
TIME_SLOTS = {
    'morning':   (6, 10),
    'afternoon': (12, 16),
    'evening':   (17, 20),
    'night':     (21, 23),
}

# Each aircraft is assigned ONE pattern — this controls which slots it flies in.
# Mix of single-slot and multi-slot patterns, matching a real airline's mix of
# short-haul (multiple flights/day) vs long-haul (once a day) aircraft.
FLIGHT_PATTERNS = [
    ['morning'],
    ['afternoon'],
    ['evening'],
    ['night'],
    ['morning', 'afternoon'],
    ['morning', 'evening'],
    ['afternoon', 'night'],
    ['morning', 'afternoon', 'evening'],  # busy short-haul aircraft
]


class Command(BaseCommand):
    help = 'Seeds 65 flights with realistic time-of-day scheduling patterns'

    def handle(self, *args, **kwargs):
        Flight.objects.all().delete()
        now = timezone.now()
        count = 0
        flight_num = 100

        for aircraft_id in range(1, 66):  # 65 aircraft total
            origin, destination = random.choice(ASIA_ROUTES)
            pattern = random.choice(FLIGHT_PATTERNS)

            # Some aircraft only fly every alternate day, some daily —
            # keeps it realistic instead of every aircraft flying every single day
            days_ahead = random.choice([1, 1, 2, 3])  # weighted toward "tomorrow"

            for slot in pattern:
                start_hour, end_hour = TIME_SLOTS[slot]
                dep_hour = random.randint(start_hour, end_hour)
                dep_minute = random.choice([0, 15, 30, 45])

                dep = (now + timedelta(days=days_ahead)).replace(
                    hour=dep_hour, minute=dep_minute, second=0, microsecond=0
                )

                flight_num += 1
                Flight.objects.create(
                    flight_number=f"SJ{flight_num}",
                    origin=origin,
                    destination=destination,
                    departure_time=dep,
                    arrival_time=dep + timedelta(hours=random.randint(1, 5)),
                    status='Scheduled',
                    seats_available=random.randint(20, 180),
                )
                count += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {count} flights across 65 aircraft with time-slot scheduling.'
        ))