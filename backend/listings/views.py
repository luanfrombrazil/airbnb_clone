from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import filter_properties
from .models import Property, PropertyImage, Reservation
from .permissions import IsHostOrReadOnly
from .serializers import (
    PropertyImageSerializer,
    PropertySerializer,
    ReservationSerializer,
)


class PropertyViewSet(viewsets.ModelViewSet):
    """
    /api/properties/ — leitura pública (visitante pode buscar, filtrar e ver o mapa).
    Criar/editar exige estar logado como anfitrião dono do imóvel.
    """

    serializer_class = PropertySerializer
    permission_classes = [IsHostOrReadOnly]

    def get_queryset(self):
        queryset = Property.objects.prefetch_related("images").select_related("host")
        return filter_properties(queryset, self.request.query_params)

    def perform_create(self, serializer):
        serializer.save(host=self.request.user)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def mine(self, request):
        """Imóveis do anfitrião logado (painel de controle)."""
        queryset = Property.objects.filter(host=request.user).prefetch_related("images")
        return Response(self.get_serializer(queryset, many=True).data)


class PropertyImageViewSet(viewsets.ModelViewSet):
    """Fotos dos imóveis. Só o dono do imóvel pode mexer."""

    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    permission_classes = [IsHostOrReadOnly]


class ReservationViewSet(viewsets.ModelViewSet):
    """
    /api/reservations/ — o hóspede vê e cria as suas; o anfitrião vê as
    solicitações recebidas nos seus imóveis e pode aprovar ou recusar.
    """

    serializer_class = ReservationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base = Reservation.objects.select_related("property", "guest")
        if user.is_host:
            return base.filter(property__host=user)
        return base.filter(guest=user)

    def perform_create(self, serializer):
        serializer.save(guest=self.request.user)

    def _decide(self, request, pk, novo_status):
        reserva = self.get_object()
        if reserva.property.host_id != request.user.id:
            return Response(
                {"detail": "Apenas o anfitrião do imóvel pode responder."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if reserva.status != "PENDING":
            return Response(
                {"detail": "Esta solicitação já foi respondida."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reserva.status = novo_status
        reserva.save()
        return Response(self.get_serializer(reserva).data)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        return self._decide(request, pk, "APPROVED")

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._decide(request, pk, "REJECTED")
