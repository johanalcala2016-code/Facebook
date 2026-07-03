from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator
from django.utils import timezone

class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', blank=True, null=True)
    amigos = models.ManyToManyField(User, related_name='mis_amigos', blank=True)
    ultima_conexion = models.DateTimeField(default=timezone.now) # 🆕 Campo para rastrear el estado Online

    def __str__(self):
        return f"Perfil de {self.usuario.username}"

    # 🆕 Función helper para saber si está conectado ahora mismo (menos de 5 minutos)
    def esta_online(self):
        if self.ultima_conexion:
            return timezone.now() - self.ultima_conexion < timezone.timedelta(minutes=5)
        return False

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.get_or_create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    if hasattr(instance, 'perfil'):
        instance.perfil.save()

class Publicacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='publicaciones')
    contenido = models.TextField(max_length=500)
    # 🆕 Campo para subir imágenes de forma opcional (blank=True, null=True)
    # 🆕 Cambiamos a FileField y agregamos el validador para admitir imágenes comunes y videos mp4
    archivo = models.FileField(
        upload_to='posts/', 
        blank=True, 
        null=True, 
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'mp4'])]
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='posts_gustados', blank=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.usuario.username} - {self.contenido[:20]}..."
        
    def total_likes(self):
        return self.likes.count()

class Comentario(models.Model):
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField(max_length=300)
    imagen = models.ImageField(upload_to='comentarios/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha_creacion']

    def __str__(self):
        return f"Comentario de {self.usuario.username} en Post {self.publicacion.id}"

class SolicitudAmistad(models.Model):
    remitente = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes_enviadas')
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes_recibidas')
    creada = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"De {self.remitente.username} para {self.destinatario.username}"
# Create your models here.

class PublicacionCompartida(models.Model):
    usuario_que_comparte = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compartidos')
    publicacion_original = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='veces_compartida')
    fecha_compartido = models.DateTimeField(auto_now_add=True)

class Historia(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='historias')
    # Usamos FileField para que puedan subir tanto fotos como videos .mp4 en sus historias
    archivo = models.FileField(upload_to='stories/')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Historia de {self.usuario.username} - {self.fecha_creacion}"