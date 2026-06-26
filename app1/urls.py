from django.urls import path
from . import views

urlpatterns = [
    path('', views.feed_home, name='feed'),
    path('like/<int:post_id>/', views.dar_like, name='dar_like'),
    path('comentar/<int:post_id>/', views.agregar_comentario, name='agregar_comentario'),
]
