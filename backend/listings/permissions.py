from rest_framework import permissions


class IsHostOrReadOnly(permissions.BasePermission):
    """Qualquer um lê; só anfitriões criam, e só o dono edita/apaga."""

    message = "Você só pode gerenciar os seus próprios imóveis."

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user.is_authenticated and request.user.is_host)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # obj pode ser um Property ou uma PropertyImage
        host_id = getattr(obj, "host_id", None) or obj.property.host_id
        return host_id == request.user.id
