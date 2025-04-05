# SmartFly by Zayn Bux

A modern airline integration service built with Django and Django REST Framework.
This project demonstrates a sophisticated backend system for managing airline bookings,
flights, and passenger information with real-time integration capabilities.

*   **Backend Framework:** Python (Django)
*   **API Development:** Django REST Framework for creating RESTful APIs.
*   **Database:** PostgreSQL (Relational Database)
*   **Caching/Queueing:** Redis (Used here for caching flight availability)
*   **API Integration:** Simulates interaction with an external service (e.g., a legacy SOAP system) for booking confirmation.
*   **Performance Tuning:** Includes examples of database query optimization (filtering, ordering, `select_related`), caching, and considerations for high traffic (atomic transactions).
*   **Containerization:** Docker and Docker Compose for easy setup and deployment.

## Project Structure

```
.
├── airline_integration_service/ # Django project directory
│   ├── __init__.py
│   ├── settings.py         # Project settings (DB, Cache, Apps)
│   ├── urls.py             # Main URL routing
│   ├── wsgi.py
│   ├── asgi.py
│   └── management/         # Custom Django commands
│       └── commands/
│           └── wait_for_db.py # Helper script for Docker Compose
├── bookings/                 # Django app for bookings
│   ├── __init__.py
│   ├── admin.py            # Admin interface configuration
│   ├── apps.py
│   ├── models.py           # Database models (Passenger, Flight, Booking)
│   ├── serializers.py      # DRF serializers for API data representation
│   ├── views.py            # API views (ViewSets)
│   ├── urls.py             # App-specific URL routing
│   ├── services.py         # Simulates external service interaction
│   ├── cache.py            # Caching logic (using Redis)
│   └── migrations/
├── .gitignore
├── Dockerfile                # Defines the application container
├── docker-compose.yml        # Orchestrates services (web, db, redis)
├── manage.py                 # Django management utility
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Features

*   **CRUD Operations:** Full CRUD for Passengers, Read-only for Flights, Create/Read/Cancel for Bookings via REST API.
*   **Database Modeling:** Relational models for Passengers, Flights, and Bookings with appropriate relationships and indexing.
*   **API Design:** RESTful API endpoints using Django REST Framework ViewSets.
*   **External API Integration:** Simulation of calling an external service during booking creation. Handles success and failure scenarios.
*   **Caching with Redis:** Caching flight availability data to reduce database load. Cache invalidation on booking confirmation/cancellation.
*   **Database Transactions:** Using `transaction.atomic` to ensure atomicity during booking creation and cancellation.
*   **Configuration Management:** Using `django-environ` to manage settings via environment variables.
*   **API Documentation:** Integrated Swagger UI for API exploration.
*   **Containerization:** Ready to run using Docker Compose.
*   **Performance Considerations:** Indexing on models, `select_related` in ViewSet querysets, efficient filtering/ordering in `FlightViewSet`, caching strategy.

## Running Locally with Docker

**Prerequisites:**

*   Docker
*   Docker Compose (usually included with Docker Desktop)

**Steps:**

1.  **Clone the repository (or ensure you have the project files).**
2.  **Navigate to the project root directory** (where `docker-compose.yml` is located) in your terminal.
3.  **Build and start the services:**
    ```bash
    docker-compose up --build -d
    ```
    *   `--build`: Forces Docker to rebuild the image if `Dockerfile` or context changes.
    *   `-d`: Runs the containers in detached mode (in the background).

4.  **Wait for services to start.** The `web` service uses the `wait_for_db.py` script, so it will wait for PostgreSQL to be ready before applying migrations and starting the Django server.
You can view logs using:
    ```bash
    docker-compose logs -f web db redis
    ```

5.  **Access the application:**
    *   **API Root:** [http://localhost:8000/api/](http://localhost:8000/api/)
    *   **Swagger API Docs:** [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
    *   **Redoc API Docs:** [http://localhost:8000/redoc/](http://localhost:8000/redoc/)
    *   **Admin Portal:** [http://localhost:8000/admin/](http://localhost:8000/admin/)
        *   To use the admin, you'll need to create a superuser:
            ```bash
            docker-compose exec web python manage.py createsuperuser
            ```
            Follow the prompts to create an admin username and password.

6.  **Populate initial data (Optional):**
    *   You can use the Django admin or the API endpoints (via Swagger UI or tools like `curl`/Postman) to create some initial `Passenger` and `Flight` data before creating `Booking`s.

7.  **Stopping the services:**
    ```bash
    docker-compose down
    ```
    *   Add `-v` if you want to remove the PostgreSQL data volume (`docker-compose down -v`).

## API Endpoints (via `/api/` prefix)

*   `/passengers/` (GET, POST)
*   `/passengers/{id}/` (GET, PUT, PATCH, DELETE)
*   `/flights/` (GET) - Supports filtering (`?origin=...`, `?destination=...`, `?departure_date=YYYY-MM-DD`) and ordering (`?ordering=price`, `?ordering=-departure_time`)
*   `/flights/{id}/` (GET)
*   `/flights/{id}/availability/` (GET) - Gets cached seat availability.
*   `/bookings/` (GET, POST) - POST creates a booking (requires `passenger_id` and `flight_id` in request body).
*   `/bookings/{id}/` (GET)
*   `/bookings/{id}/cancel/` (POST) - Cancels the booking.

## Author

Zayn Bux

## License

This project is proprietary software. All rights reserved. 