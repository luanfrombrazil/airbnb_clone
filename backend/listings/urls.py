from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PropertyImageViewSet, PropertyViewSet, ReservationViewSet

router = DefaultRouter()
router.register(r"properties", PropertyViewSet, basename="property")
router.register(r"property-images", PropertyImageViewSet)
router.register(r"reservations", ReservationViewSet, basename="reservation")

urlpatterns = [path("", include(router.urls))]
