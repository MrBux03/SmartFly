from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.shortcuts import get_object_or_404
import logging

from .models import Passenger, Flight, Booking
from .serializers import (
    PassengerSerializer, FlightSerializer,
    BookingSerializer, BookingStatusUpdateSerializer
)
from .services import simulate_external_booking_confirmation
from .cache import get_flight_availability, invalidate_flight_availability_cache

logger = logging.getLogger(__name__)

class PassengerViewSet(viewsets.ModelViewSet):
    """ API endpoint for managing Passengers. """
    queryset = Passenger.objects.all().order_by('-created_at')
    serializer_class = PassengerSerializer
    # Add permissions and authentication later if needed
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class FlightViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing Flights (Read-Only).
    Includes filtering and searching capabilities.
    Demonstrates performance tuning via optimized queries.
    """
    serializer_class = FlightSerializer
    # permission_classes = [permissions.AllowAny] # Publicly viewable flights

    def get_queryset(self):
        """ Optimize query with select_related/prefetch_related if needed later. """
        queryset = Flight.objects.all()

        # --- Performance Tuning Example: Filtering --- #
        # Efficient filtering directly on the database
        origin = self.request.query_params.get('origin')
        destination = self.request.query_params.get('destination')
        departure_date = self.request.query_params.get('departure_date') # Expects YYYY-MM-DD

        if origin:
            queryset = queryset.filter(origin__iexact=origin)
        if destination:
            queryset = queryset.filter(destination__iexact=destination)
        if departure_date:
            # Ensure proper date filtering
            try:
                queryset = queryset.filter(departure_time__date=departure_date)
            except ValueError:
                # Handle invalid date format (e.g., ignore or return error)
                pass # Or raise ValidationError

        # --- Performance Tuning Example: Ordering --- #
        # Allow ordering by specific fields
        ordering = self.request.query_params.get('ordering', 'departure_time') # Default order
        allowed_ordering_fields = ['departure_time', 'price', '-departure_time', '-price']
        if ordering in allowed_ordering_fields:
             queryset = queryset.order_by(ordering)
        else:
             queryset = queryset.order_by('departure_time') # Default safe ordering

        logger.info(f"Flight Queryset constructed with filters: origin={origin}, dest={destination}, date={departure_date}, ordering={ordering}")
        return queryset

    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        """ Custom action to get cached flight availability. """
        availability = get_flight_availability(pk)
        if availability is None:
            # Handle case where flight doesn't exist or error occurred in cache function
             return Response({"error": "Flight not found or availability could not be determined."}, status=status.HTTP_404_NOT_FOUND)
        return Response({"available_seats": availability})

class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing Bookings.
    Demonstrates transactional logic, external service integration, and caching.
    """
    queryset = Booking.objects.all().select_related('passenger', 'flight').order_by('-created_at') # Performance: Optimize default query
    serializer_class = BookingSerializer
    # permission_classes = [permissions.IsAuthenticated] # Requires authentication

    def get_queryset(self):
        """ Optionally filter bookings by user if authentication is added. """
        queryset = super().get_queryset()
        # Example: If users should only see their own bookings
        # user = self.request.user
        # if user.is_authenticated and not user.is_staff:
        #    queryset = queryset.filter(passenger__user=user) # Assuming a user link on Passenger
        return queryset

    @transaction.atomic # Ensure booking creation and external call are atomic
    def create(self, request, *args, **kwargs):
        """
        Creates a booking, places it in PENDING, then simulates external confirmation.
        Uses database transaction and handles external service response.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Serializer validation already checked flight availability (basic check)
        # For higher concurrency, a select_for_update might be needed here or during validation
        flight = serializer.validated_data['flight'] # Get validated flight object

        # Create the booking initially as PENDING
        # The serializer's save method will associate passenger and flight from IDs
        booking = serializer.save(status='PENDING')
        logger.info(f"Booking {booking.id} created with status PENDING.")

        # --- Integration with External Service --- #
        success, external_ref, error_message = simulate_external_booking_confirmation(booking)

        if success:
            booking.status = 'CONFIRMED'
            booking.external_system_ref = external_ref
            booking.save(update_fields=['status', 'external_system_ref', 'updated_at'])
            # --- Cache Invalidation --- #
            invalidate_flight_availability_cache(booking.flight.id)
            logger.info(f"Booking {booking.id} confirmed externally. Ref: {external_ref}. Cache invalidated.")
            headers = self.get_success_headers(serializer.data)
            return Response(self.get_serializer(booking).data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            # External service failed, mark booking as FAILED
            booking.status = 'FAILED'
            # Store the error message if needed (add a field to Booking model?)
            booking.save(update_fields=['status', 'updated_at'])
            logger.error(f"External confirmation failed for booking {booking.id}. Status set to FAILED. Reason: {error_message}")
            # Don't invalidate cache as the booking didn't succeed
            # Return an error response indicating the failure
            return Response(
                {"error": "Booking creation successful, but external confirmation failed.", "detail": error_message},
                status=status.HTTP_503_SERVICE_UNAVAILABLE # Or another appropriate error
            )

    # Override update/partial_update if needed, e.g., to prevent direct status changes via PUT/PATCH
    def update(self, request, *args, **kwargs):
        return Response({"detail": "Method \"PUT\" not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
         return Response({"detail": "Method \"PATCH\" not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # Custom action for cancellation (example)
    @action(detail=True, methods=['post'])
    @transaction.atomic
    def cancel(self, request, pk=None):
        """ Cancels a booking. """
        booking = self.get_object()
        if booking.status == 'CANCELLED':
            return Response({"detail": "Booking is already cancelled."}, status=status.HTTP_400_BAD_REQUEST)
        if booking.status != 'CONFIRMED' and booking.status != 'PENDING':
             return Response({"detail": f"Cannot cancel booking with status {booking.status}."}, status=status.HTTP_400_BAD_REQUEST)

        original_status = booking.status
        booking.status = 'CANCELLED'
        booking.save(update_fields=['status', 'updated_at'])

        # If it was confirmed, need to invalidate cache
        if original_status == 'CONFIRMED':
            invalidate_flight_availability_cache(booking.flight.id)
            logger.info(f"Booking {booking.id} cancelled. Cache invalidated.")
        else:
             logger.info(f"Booking {booking.id} cancelled (was PENDING).")

        # Optional: Add logic here to notify external systems about cancellation if needed

        return Response(self.get_serializer(booking).data, status=status.HTTP_200_OK)

# Example of a simpler view using generics if full ViewSet not needed
class BookingStatusView(generics.RetrieveUpdateAPIView):
    """
    Specific endpoint to view or update only the status of a booking.
    (Demonstrates alternative to full ViewSet)
    NOTE: For this project, cancellation is handled via a custom action in BookingViewSet.
          This is just an example of using generics.
    """
    queryset = Booking.objects.all()
    serializer_class = BookingStatusUpdateSerializer # Use a dedicated serializer
    lookup_field = 'pk' # or 'booking_reference'?
    # permission_classes = [permissions.IsAdminUser] # Example: Only admins can force status changes

    def update(self, request, *args, **kwargs):
        # Implement custom logic for status update if needed,
        # including validation, side effects (cache invalidation), etc.
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True) # Allow partial update
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data.get('status')
        old_status = instance.status

        # --- Add business logic for status transitions --- #
        if new_status == old_status:
             return Response(self.get_serializer(instance).data) # No change

        # Example: Prevent changing from CANCELLED or FAILED
        if old_status in ['CANCELLED', 'FAILED']:
            return Response({"error": f"Cannot change status from {old_status}"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            instance.status = new_status
            instance.save(update_fields=['status', 'updated_at'])

            # Invalidate cache if booking becomes confirmed or un-confirmed
            if (new_status == 'CONFIRMED' and old_status != 'CONFIRMED') or \
               (old_status == 'CONFIRMED' and new_status != 'CONFIRMED'):
                invalidate_flight_availability_cache(instance.flight.id)
                logger.info(f"Booking {instance.id} status changed to {new_status}. Cache invalidated.")
            else:
                logger.info(f"Booking {instance.id} status changed to {new_status}.")

        return Response(self.get_serializer(instance).data) 