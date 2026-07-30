from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyViewSet, ReservationViewSet, PropertyImageViewSet

router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'reservations', ReservationViewSet, basename='reservation')
router.register(r'images', PropertyImageViewSet, basename='propertyimage')

urlpatterns = [
    path('', include(router.urls)),
]