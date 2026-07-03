from django.urls import path
from django.contrib.auth import views as auth_views
from . import views


urlpatterns = [
    path('', views.feed_home, name='feed'),
    path('like/<int:post_id>/', views.dar_like, name='dar_like'),
    path('comentar/<int:post_id>/', views.agregar_comentario, name='agregar_comentario'),
    path('solicitud/aceptar/<int:solicitud_id>/', views.aceptar_solicitud, name='aceptar_solicitud'),
    path('solicitud/enviar/<int:usuario_id>/', views.enviar_solicitud, name='enviar_solicitud'),
    path('post/eliminar/<int:post_id>/', views.eliminar_post, name='eliminar_post'), # 🆕 URL nueva
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('post/compartir/<int:post_id>/', views.compartir_post, name='compartir_post'),
]