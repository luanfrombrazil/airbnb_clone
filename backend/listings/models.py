from django.db import models
from django.conf import settings

class Property(models.Model):
    host = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=255)
    description = models.TextField()
    address = models.CharField(max_length=255)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    max_guests = models.IntegerField()
    amenities = models.JSONField(default=list)

class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')

class Reservation(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pendente'),
        ('APPROVED', 'Aprovada'),
        ('REJECTED', 'Recusada'),
    )
    guest = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reservations')
    check_in = models.DateField()
    check_out = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    payment_info = models.JSONField()