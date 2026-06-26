from django.db import models
from django.contrib.auth.models import User

class Publicacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='publicaciones')
    contenido = models.TextField(max_length=500)
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
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['fecha_creacion']

    def __str__(self):
        return f"Comentario de {self.usuario.username} en Post {self.publicacion.id}"
# Create your models here.
