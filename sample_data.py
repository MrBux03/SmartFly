from django.utils import timezone
from datetime import timedelta
from bookings.models import Passenger, Flight, Booking
import random

# Create sample passengers
passengers = [
    {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'date_of_birth': '1990-01-15'
    },
    {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'email': 'jane.smith@example.com',
        'date_of_birth': '1985-03-20'
    },
    {
        'first_name': 'Michael',
        'last_name': 'Johnson',
        'email': 'michael.j@example.com',
        'date_of_birth': '1995-07-10'
    }
]

# Create sample flights
flights = [
    {
        'flight_number': 'SA101',
        'origin': 'Johannesburg',
        'destination': 'Cape Town',
        'departure_time': timezone.now() + timedelta(days=1),
        'arrival_time': timezone.now() + timedelta(days=1, hours=2),
        'total_seats': 150,
        'price': '1200.00'
    },
    {
        'flight_number': 'SA202',
        'origin': 'Cape Town',
        'destination': 'Durban',
        'departure_time': timezone.now() + timedelta(days=2),
        'arrival_time': timezone.now() + timedelta(days=2, hours=1, minutes=30),
        'total_seats': 120,
        'price': '900.00'
    },
    {
        'flight_number': 'SA303',
        'origin': 'Durban',
        'destination': 'Johannesburg',
        'departure_time': timezone.now() + timedelta(days=3),
        'arrival_time': timezone.now() + timedelta(days=3, hours=1, minutes=45),
        'total_seats': 180,
        'price': '1100.00'
    }
]

# Create the passengers
created_passengers = []
for passenger_data in passengers:
    passenger, created = Passenger.objects.get_or_create(
        email=passenger_data['email'],
        defaults=passenger_data
    )
    created_passengers.append(passenger)
    print(f"{'Created' if created else 'Retrieved'} passenger: {passenger.first_name} {passenger.last_name}")

# Create the flights
created_flights = []
for flight_data in flights:
    flight, created = Flight.objects.get_or_create(
        flight_number=flight_data['flight_number'],
        defaults=flight_data
    )
    created_flights.append(flight)
    print(f"{'Created' if created else 'Retrieved'} flight: {flight.flight_number} from {flight.origin} to {flight.destination}")

# Create some sample bookings
bookings_data = [
    (created_passengers[0], created_flights[0]),  # John books JHB -> CPT
    (created_passengers[1], created_flights[1]),  # Jane books CPT -> DUR
    (created_passengers[2], created_flights[2]),  # Michael books DUR -> JHB
]

for passenger, flight in bookings_data:
    booking, created = Booking.objects.get_or_create(
        passenger=passenger,
        flight=flight,
        defaults={
            'status': 'CONFIRMED',
            'seat_number': f"{random.randint(1, 30)}{chr(random.randint(65, 70))}"  # e.g., 15A
        }
    )
    print(f"{'Created' if created else 'Retrieved'} booking: {booking.booking_reference} for {passenger.first_name} on flight {flight.flight_number}")

print("\nSample data creation completed!") 