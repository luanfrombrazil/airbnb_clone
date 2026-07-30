from datetime import date

from rest_framework import serializers

from users.serializers import UserSerializer

from .models import Property, PropertyImage, Reservation


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ["id", "property", "url"]

    def validate_property(self, imovel):
        # Impede que um anfitrião adicione fotos ao imóvel de outra pessoa.
        if imovel.host_id != self.context["request"].user.id:
            raise serializers.ValidationError("Este imóvel não é seu.")
        return imovel


class PropertySerializer(serializers.ModelSerializer):
    images = PropertyImageSerializer(many=True, read_only=True)
    host = UserSerializer(read_only=True)
    booked_dates = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "id",
            "host",
            "title",
            "description",
            "address",
            "city",
            "price_per_night",
            "max_guests",
            "amenities",
            "rating",
            "images",
            "booked_dates",
            "created_at",
        ]
        # host é somente-leitura pela declaração acima: vem do usuário logado
        read_only_fields = ["id", "rating", "created_at"]

    def get_booked_dates(self, obj):
        return obj.booked_dates()


class ReservationSerializer(serializers.ModelSerializer):
    property_detail = PropertySerializer(source="property", read_only=True)
    guest = UserSerializer(read_only=True)
    nights = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id",
            "property",
            "property_detail",
            "guest",
            "check_in",
            "check_out",
            "guests_count",
            "nights",
            "total_price",
            "status",
            "status_display",
            "created_at",
        ]
        # o status só muda pelas ações aprovar/recusar do anfitrião
        read_only_fields = ["id", "status", "created_at"]

    def validate(self, attrs):
        prop = attrs["property"]
        check_in, check_out = attrs["check_in"], attrs["check_out"]

        if check_out <= check_in:
            raise serializers.ValidationError(
                {"check_out": "A saída deve ser depois da entrada."}
            )
        if check_in < date.today():
            raise serializers.ValidationError(
                {"check_in": "A entrada não pode ser no passado."}
            )
        if attrs.get("guests_count", 1) > prop.max_guests:
            raise serializers.ValidationError(
                {"guests_count": f"O imóvel acomoda até {prop.max_guests} hóspede(s)."}
            )
        if prop.host_id == self.context["request"].user.id:
            raise serializers.ValidationError(
                {"property": "Você não pode reservar o seu próprio imóvel."}
            )
        if not prop.is_available(check_in, check_out):
            raise serializers.ValidationError(
                {"check_in": "O imóvel já está reservado nesse período."}
            )
        return attrs
