import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

def simulate_external_booking_confirmation(booking):
    """
    Simulates calling an external booking system (like a legacy SOAP service).

    In a real scenario, this would involve using a SOAP client (like zeep)
    to construct and send a request, then parse the response.
    Here, we just simulate success/failure.

    Args:
        booking (Booking): The booking object.

    Returns:
        tuple: (success: bool, external_ref: str | None, error_message: str | None)
    """
    url = settings.EXTERNAL_BOOKING_SERVICE_URL
    timeout = settings.EXTERNAL_SERVICE_TIMEOUT

    payload = {
        # Simulate SOAP-like structure or relevant data
        "bookingRequest": {
            "passengerDetails": {
                "firstName": booking.passenger.first_name,
                "lastName": booking.passenger.last_name,
                "email": booking.passenger.email,
                "dob": booking.passenger.date_of_birth.isoformat(),
            },
            "flightDetails": {
                "flightNumber": booking.flight.flight_number,
                "origin": booking.flight.origin,
                "destination": booking.flight.destination,
                "departure": booking.flight.departure_time.isoformat(),
            },
            "internalBookingRef": str(booking.id),
        }
    }

    logger.info(f"Simulating external API call for booking {booking.id} to {url}")

    try:
        # In a real SOAP call,use a SOAP client library here.
        # Simulate with a simple POST request.

        # Simulate different outcomes (e.g., 80% success)
        import random
        if random.random() < 0.9: # 90% chance of success
            # Simulate successful response
            external_ref = f"EXT-{booking.booking_reference}-{random.randint(1000, 9999)}"
            logger.info(f"External service simulation SUCCESS for booking {booking.id}. Ref: {external_ref}")
            return True, external_ref, None
        else:
            # Simulate failure response
            error_message = "Simulated external service error: Capacity exceeded."
            logger.warning(f"External service simulation FAILED for booking {booking.id}: {error_message}")
            return False, None, error_message

    except requests.exceptions.RequestException as e:
        # Handle network errors, timeouts, etc.
        error_message = f"Network error contacting external service: {e}"
        logger.error(f"External service call FAILED for booking {booking.id}: {error_message}")
        return False, None, error_message
    except Exception as e:
        # Handle unexpected errors during simulation/call
        error_message = f"Unexpected error during external service call: {e}"
        logger.error(f"External service call FAILED for booking {booking.id}: {error_message}")
        return False, None, error_message 