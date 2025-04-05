from django.db import models
import uuid

class Passenger(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

class Flight(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    flight_number = models.CharField(max_length=10, unique=True)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    total_seats = models.PositiveIntegerField(default=150)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.flight_number}: {self.origin} -> {self.destination}"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('FAILED', 'Failed'), # Added for integration failures
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE, related_name='bookings')
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='bookings')
    booking_reference = models.CharField(max_length=6, unique=True, blank=True) # Often a short code
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    seat_number = models.CharField(max_length=4, blank=True, null=True) # e.g., 12A
    external_system_ref = models.CharField(max_length=255, blank=True, null=True) # For external service ID
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            # Generate a simple pseudo-random reference
            import random
            import string
            self.booking_reference = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Booking {self.booking_reference} for {self.passenger} on {self.flight}"

    class Meta:
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['flight', 'passenger']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-created_at'] 