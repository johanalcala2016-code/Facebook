from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Publicacion, Comentario, SolicitudAmistad, Perfil, PublicacionCompartida, Historia # 🆕 Añadido Historia
from .forms import RegistroUsuarioForm

def registrar_usuario(request):
    """
    Crea un nuevo usuario, guarda su nombre/apellido, 
    y lo loguea automáticamente en la sesión.
    """
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Encriptar la contraseña de forma segura
            user.set_password(form.cleaned_data['password'])
            user.save() # Aquí se dispara tu señal post_save para crear el Perfil
            
            # Loguear automáticamente tras registrarse
            login(request, user)
            return redirect('feed_home')
    else:
        form = RegistroUsuarioForm()
        
    return render(request, 'registro.html', {'form': form})

@login_required
# app1/views.py

@login_required
def feed_home(request):
    # ➡️ 1. CAPTURAR Y CREAR NUEVA PUBLICACIÓN (Movido aquí arriba)
    if request.method == 'POST' and 'contenido_post' in request.POST:
        texto = request.POST.get('contenido_post')
        imagen = request.FILES.get('archivo')
        
        if texto or imagen:
            Publicacion.objects.create(
                usuario=request.user,
                contenido=texto,
                archivo=imagen
            )
            return redirect('feed_home')
    
    # ... resto de tu código de feed_home ...
    if request.method == 'POST' and 'subir_historia' in request.POST:
        archivo_historia = request.FILES.get('archivo_historia')
        if archivo_historia:
            Historia.objects.create(usuario=request.user, archivo=archivo_historia)
        return redirect('feed_home')

    # 2. Filtro de historias de las últimas 24 horas
    hace_24_horas = timezone.now() - timedelta(hours=24)
    historias_activas = Historia.objects.filter(fecha_creacion__gte=hace_24_horas).order_by('-fecha_creacion')

    # 3. Lógica del buscador y Posts del Feed (Ordenados de más reciente a más antiguo)
    busqueda = request.GET.get('q')
    usuarios_encontrados = []
    
    if busqueda:  # 👈 ¡ESTE CONDICIONAL EVITA EL ERROR DE NONE!
        usuarios_encontrados = User.objects.filter(username__icontains=busqueda).exclude(id=request.user.id)
        todos_los_posts = Publicacion.objects.filter(
            Q(contenido__icontains=busqueda) | Q(usuario__username__icontains=busqueda)
        ).order_by('-fecha_creacion')  # 👈 Asegúrate de si tu campo es 'fecha_creacion' o 'fecha_publicacion'

        posts_compartidos = PublicacionCompartida.objects.filter(
            Q(publicacion_original__contenido__icontains=busqueda) | 
            Q(usuario_que_comparte__username__icontains=busqueda)
        ).order_by('-fecha_compartido')
    else:
        # Aquí es donde va lo que buscabas originalmente:
        todos_los_posts = Publicacion.objects.all().order_by('-fecha_creacion')
        posts_compartidos = PublicacionCompartida.objects.all().order_by('-fecha_compartido')

    # 4. Otras consultas necesarias
    solicitudes = SolicitudAmistad.objects.filter(destinatario=request.user)
    mis_amigos = request.user.perfil.amigos.all()

    # 5. UN SOLO CONTEXTO Y UN SOLO RETURN
    contexto = {
        'posts': todos_los_posts,
        'posts_compartidos': posts_compartidos,
        'historias': historias_activas,
        'solicitudes': solicitudes,
        'mis_amigos': mis_amigos,
        'busqueda': busqueda,
        'usuarios_encontrados': usuarios_encontrados,
    }
    return render(request, 'feed.html', contexto)

@login_required
def dar_like_post(request, post_id):
    if request.method == "POST" and request.user.is_authenticated:
        post = get_object_or_404(Publicacion, id=post_id)
        if post.likes.filter(id=request.user.id).exists():
            post.likes.remove(request.user)
        else:
            post.likes.add(request.user)
    return redirect('feed_home')

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
    return redirect('feed_home')

@login_required
def aceptar_solicitud(request, solicitud_id):
    if request.method == 'POST':
        solicitud = get_object_or_404(SolicitudAmistad, id=solicitud_id, destinatario=request.user)
        perfil_receptor, _ = Perfil.objects.get_or_create(usuario=request.user)
        perfil_emisor, _ = Perfil.objects.get_or_create(usuario=solicitud.remitente)
        
        perfil_receptor.amigos.add(solicitud.remitente)
        perfil_emisor.amigos.add(request.user)
        solicitud.delete()
    return redirect('feed_home')

@login_required
def enviar_solicitud(request, usuario_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=usuario_id)
        SolicitudAmistad.objects.get_or_create(remitente=request.user, destinatario=target_user)
    return redirect('feed_home')

@login_required
def eliminar_post(request, post_id):
    if request.method == 'POST':
        # Buscamos el post, asegurándonos de que pertenezca al usuario que intenta borrarlo
        post = get_object_or_404(Publicacion, id=post_id, usuario=request.user)
        post.delete()
    return redirect('feed_home')

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
        
    return redirect('feed_home')
# Create your views here. 
