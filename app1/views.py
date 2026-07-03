from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Publicacion, Comentario, SolicitudAmistad, Perfil, PublicacionCompartida

@login_required
def feed_home(request):
    Perfil.objects.get_or_create(usuario=request.user)
    
    if request.method == 'POST':
        texto = request.POST.get('contenido_post')
        imagen_subida = request.FILES.get('archivo') # 🛠️ Corregido: Ahora coincide con el name="archivo" de tu HTML # Captura multimedia
        
        if texto or imagen_subida:
            Publicacion.objects.create(
                usuario=request.user, 
                contenido=texto if texto else "",
                archivo=imagen_subida  # 🛠️ Corregido: cambiamos 'imagen' por 'archivo'
            )
            return redirect('feed')

    busqueda = request.GET.get('q')
    usuarios_encontrados = None # Cambiado a None por defecto
    
    if busqueda:
        todos_los_posts = Publicacion.objects.filter(
            Q(contenido__icontains=busqueda) | Q(usuario__username__icontains=busqueda)
        )
        usuarios_encontrados = User.objects.filter(username__icontains=busqueda).exclude(id=request.user.id)
    else:
        # Si no hay búsqueda, trae absolutamente todos los posts para el feed principal
        todos_los_posts = Publicacion.objects.all()

    solicitudes = SolicitudAmistad.objects.filter(destinatario=request.user)
    mis_amigos = request.user.perfil.amigos.all()

    contexto = {
        'posts': todos_los_posts,
        'solicitudes': solicitudes,
        'mis_amigos': mis_amigos,
        'busqueda': busqueda,
        'usuarios_encontrados': usuarios_encontrados,
    }
    return render(request, 'feed.html', contexto)

@login_required
def dar_like(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Publicacion, id=post_id)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
    return redirect('feed')

@login_required
def agregar_comentario(request, post_id):
    if request.method == 'POST':
        texto = request.POST.get('contenido_comentario')
        imagen_subida = request.FILES.get('imagen_comentario') # 🆕 Captura la imagen del comentario
        
        if texto or imagen_subida:
            post = get_object_or_404(Publicacion, id=post_id)
            Comentario.objects.create(
                publicacion=post, 
                usuario=request.user, 
                contenido=texto if texto else "",
                imagen=imagen_subida
            )
    return redirect('feed')

@login_required
def aceptar_solicitud(request, solicitud_id):
    if request.method == 'POST':
        solicitud = get_object_or_404(SolicitudAmistad, id=solicitud_id, destinatario=request.user)
        perfil_receptor, _ = Perfil.objects.get_or_create(usuario=request.user)
        perfil_emisor, _ = Perfil.objects.get_or_create(usuario=solicitud.remitente)
        
        perfil_receptor.amigos.add(solicitud.remitente)
        perfil_emisor.amigos.add(request.user)
        solicitud.delete()
    return redirect('feed')

@login_required
def enviar_solicitud(request, usuario_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=usuario_id)
        SolicitudAmistad.objects.get_or_create(remitente=request.user, destinatario=target_user)
    return redirect('feed')

@login_required
def eliminar_post(request, post_id):
    if request.method == 'POST':
        # Buscamos el post, asegurándonos de que pertenezca al usuario que intenta borrarlo
        post = get_object_or_404(Publicacion, id=post_id, usuario=request.user)
        post.delete()
    return redirect('feed')

@login_required
def compartir_post(request, post_id):
    if request.method == 'POST':
        post_original = get_object_or_404(Publicacion, id=post_id)
        
        # Creamos una nueva publicación para el usuario actual que copia el contenido
        Publicacion.objects.create(
            usuario=request.user,
            contenido=f"🔄 Compartió la publicación de {post_original.usuario.username}:\n\n{post_original.contenido}",
            archivo=post_original.archivo if post_original.archivo else None
        )
        
        # Registramos el evento en nuestro modelo de control
        PublicacionCompartida.objects.create(
            usuario_que_comparte=request.user,
            publicacion_original=post_original
        )
        
    return redirect('feed')
# Create your views here.
