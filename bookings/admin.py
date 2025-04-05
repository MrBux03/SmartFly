from django.contrib import admin
from .models import Passenger, Flight, Booking

@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'date_of_birth', 'created_at')
    search_fields = ('first_name', 'last_name', 'email')
    list_filter = ('created_at',)

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('id', 'flight_number', 'origin', 'destination', 'departure_time', 'arrival_time', 'price', 'total_seats', 'created_at')
    search_fields = ('flight_number', 'origin', 'destination')
    list_filter = ('departure_time', 'origin', 'destination')
    ordering = ('departure_time',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'booking_reference', 'passenger', 'flight', 'status', 'seat_number', 'external_system_ref', 'created_at')
    search_fields = ('booking_reference', 'passenger__email', 'passenger__last_name', 'flight__flight_number')
    list_filter = ('status', 'created_at', 'flight__origin', 'flight__destination')
    autocomplete_fields = ('passenger', 'flight') # Makes selection easier in admin
    ordering = ('-created_at',)
    list_select_related = ('passenger', 'flight') # Optimize admin queries 