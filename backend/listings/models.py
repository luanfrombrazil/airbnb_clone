from datetime import timedelta

from django.conf import settings
from django.db import models


class Property(models.Model):
    """Imóvel anunciado por um anfitrião."""

    host = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="properties"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=120)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    max_guests = models.PositiveIntegerField(default=1)
    amenities = models.JSONField(default=list, blank=True)
    rating = models.FloatField(default=0)  # usado para ordenar a home
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-rating", "-created_at"]
        verbose_name_plural = "properties"

    def __str__(self):
        return f"{self.title} - {self.city}"

    def booked_dates(self):
        """Datas já ocupadas por reservas aprovadas, para pintar o calendário."""
        dates = []
        for r in self.reservations.filter(status="APPROVED"):
            day = r.check_in
            while day < r.check_out:  # o dia da saída fica livre
                dates.append(day.isoformat())
                day += timedelta(days=1)
        return dates

    def is_available(self, check_in, check_out):
        """Há conflito quando inicio_A < fim_B e fim_A > inicio_B."""
        return not self.reservations.filter(
            status="APPROVED", check_in__lt=check_out, check_out__gt=check_in
        ).exists()


class PropertyImage(models.Model):
    """Foto do imóvel, referenciada por URL (evita lidar com upload de arquivo)."""

    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="images"
    )
    url = models.URLField(max_length=500)

    def __str__(self):
        return self.url


class Reservation(models.Model):
    STATUS_CHOICES = (
        ("PENDING", "Pendente"),
        ("APPROVED", "Aprovada"),
        ("REJECTED", "Recusada"),
    )

    guest = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reservations"
    )
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name="reservations"
    )
    check_in = models.DateField()
    check_out = models.DateField()
    guests_count = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.property.title} - {self.get_status_display()}"

    # Atenção: o campo "property" acima sobrescreve o decorador @property do
    # Python dentro desta classe, então estes são métodos comuns. O DRF chama
    # métodos sem argumentos automaticamente, então o serializer continua igual.
    def nights(self):
        return (self.check_out - self.check_in).days

    def total_price(self):
        return self.property.price_per_night * self.nights()
