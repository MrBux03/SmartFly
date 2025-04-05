from rest_framework import serializers
from .models import Passenger, Flight, Booking

class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ('id', 'first_name', 'last_name', 'email', 'date_of_birth', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

class FlightSerializer(serializers.ModelSerializer):
    available_seats = serializers.SerializerMethodField()

    class Meta:
        model = Flight
        fields = (
            'id', 'flight_number', 'origin', 'destination', 'departure_time',
            'arrival_time', 'price', 'total_seats', 'available_seats', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'available_seats', 'created_at', 'updated_at')

    def get_available_seats(self, obj):
        # Basic calculation, could be optimized with annotation in the viewset
        booked_seats = Booking.objects.filter(flight=obj, status='CONFIRMED').count()
        return obj.total_seats - booked_seats

class BookingSerializer(serializers.ModelSerializer):
    passenger = PassengerSerializer(read_only=True) # Nested read-only representation
    flight = FlightSerializer(read_only=True)       # Nested read-only representation
    passenger_id = serializers.UUIDField(write_only=True)
    flight_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Booking
        fields = (
            'id', 'booking_reference', 'passenger', 'flight',
            'passenger_id', 'flight_id', # Write-only fields for creating/updating
            'status', 'seat_number', 'external_system_ref',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'booking_reference', 'passenger', 'flight',
            'status', 'external_system_ref', # Status managed by backend logic
            'created_at', 'updated_at'
        )
        # Ensure write_only fields are used for input
        extra_kwargs = {
            'passenger_id': {'source': 'passenger', 'write_only': True},
            'flight_id': {'source': 'flight', 'write_only': True},
        }

    def validate(self, data):
        # Check if flight and passenger exist
        try:
            passenger = Passenger.objects.get(pk=data['passenger'])
        except Passenger.DoesNotExist:
            raise serializers.ValidationError({"passenger_id": "Passenger not found."})

        try:
            flight = Flight.objects.get(pk=data['flight'])
        except Flight.DoesNotExist:
            raise serializers.ValidationError({"flight_id": "Flight not found."}) 

        # Check for available seats (simplified check)
        booked_seats = Booking.objects.filter(flight=flight, status='CONFIRMED').count()
        if booked_seats >= flight.total_seats:
            raise serializers.ValidationError({"flight_id": "No available seats on this flight."}) 

        # Prevent duplicate bookings for the same passenger on the same flight
        if Booking.objects.filter(passenger=passenger, flight=flight, status__in=['PENDING', 'CONFIRMED']).exists():
             raise serializers.ValidationError("Passenger already has a booking on this flight.")

        data['passenger'] = passenger
        data['flight'] = flight    
        return data

class BookingStatusUpdateSerializer(serializers.Serializer): # Non-model serializer
    status = serializers.ChoiceField(choices=Booking.STATUS_CHOICES)
    # Potentially add fields for cancellation reasons, etc. 