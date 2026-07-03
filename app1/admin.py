from django.contrib import admin
from .models import Publicacion, Comentario, SolicitudAmistad, Perfil
from .models import Historia

admin.site.register(Publicacion)
admin.site.register(Comentario)
admin.site.register(SolicitudAmistad)
admin.site.register(Perfil)
admin.site.register(Historia)
# Register your models here.
