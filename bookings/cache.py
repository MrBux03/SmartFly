from django.core.cache import cache
from .models import Flight, Booking
import logging

logger = logging.getLogger(__name__)

CACHE_TIMEOUT_FLIGHT_AVAILABILITY = 60 * 5 # Cache for 5 minutes
CACHE_KEY_FLIGHT_AVAILABILITY = "flight_availability_{flight_id}"

def get_flight_availability(flight_id):
    """
    Gets the available seats for a flight, using cache if possible.
    Demonstrates Redis usage as cache.
    """
    cache_key = CACHE_KEY_FLIGHT_AVAILABILITY.format(flight_id=flight_id)
    availability = cache.get(cache_key)

    if availability is None:
        logger.info(f"Cache miss for flight availability: {flight_id}")
        try:
            flight = Flight.objects.get(pk=flight_id)
            # More performant count using the database
            # select_for_update if expecting high concurrency to avoid race conditions during booking
            booked_seats = Booking.objects.filter(flight=flight, status='CONFIRMED').count()
            availability = flight.total_seats - booked_seats
            cache.set(cache_key, availability, CACHE_TIMEOUT_FLIGHT_AVAILABILITY)
            logger.info(f"Calculated and cached flight availability for {flight_id}: {availability}")
        except Flight.DoesNotExist:
            logger.warning(f"Attempted to get availability for non-existent flight: {flight_id}")
            return None # Or raise an error
    else:
        logger.info(f"Cache hit for flight availability: {flight_id}")

    return availability

def invalidate_flight_availability_cache(flight_id):
    """
    Invalidates the cache for a specific flight's availability.
    Call this after a booking is confirmed or cancelled.
    """
    cache_key = CACHE_KEY_FLIGHT_AVAILABILITY.format(flight_id=flight_id)
    logger.info(f"Invalidating cache for flight availability: {flight_id}")
    cache.delete(cache_key) 