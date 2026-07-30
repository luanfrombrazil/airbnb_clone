"""Filtros da barra de pesquisa, aplicados sobre a queryset de imóveis."""


def filter_properties(queryset, params):
    city = params.get("city")
    if city:
        queryset = queryset.filter(city__icontains=city)

    min_price = params.get("min_price")
    if min_price:
        queryset = queryset.filter(price_per_night__gte=min_price)

    max_price = params.get("max_price")
    if max_price:
        queryset = queryset.filter(price_per_night__lte=max_price)

    # Datas: remove imóveis com reserva aprovada que colida com o período
    check_in, check_out = params.get("check_in"), params.get("check_out")
    if check_in and check_out:
        queryset = queryset.exclude(
            reservations__status="APPROVED",
            reservations__check_in__lt=check_out,
            reservations__check_out__gt=check_in,
        )

    return queryset.distinct()
