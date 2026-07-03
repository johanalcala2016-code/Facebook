from django.utils import timezone
from .models import Perfil

class ActividadUsuarioMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Si el usuario inició sesión, actualizamos su última conexión
        if request.user.is_authenticated:
            Perfil.objects.filter(usuario=request.user).update(ultima_conexion=timezone.now())
        
        response = self.get_response(request)
        return response