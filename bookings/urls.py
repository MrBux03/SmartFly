from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PassengerViewSet, FlightViewSet, BookingViewSet, BookingStatusView

# Create a router and register viewsets with it.
router = DefaultRouter()
router.register(r'passengers', PassengerViewSet, basename='passenger')
router.register(r'flights', FlightViewSet, basename='flight')
router.register(r'bookings', BookingViewSet, basename='booking')

# The API URLs are now determined automatically by the router.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    # Example of including a non-viewset view (not used by default in this setup)
    # path('bookings/<uuid:pk>/status/', BookingStatusView.as_view(), name='booking-status'),
] 