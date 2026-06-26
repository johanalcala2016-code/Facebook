from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Publicacion, Comentario  # 👈 ¡Aquí está la solución al error!

@login_required
def feed_home(request):
    if request.method == 'POST':
        texto = request.POST.get('contenido_post')
        if texto:
            Publicacion.objects.create(
                usuario=request.user,
                contenido=texto
            )
            return redirect('feed') 

    todos_los_posts = Publicacion.objects.all()
    contexto = {
        'posts': todos_los_posts
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
        if texto:
            post = get_object_or_404(Publicacion, id=post_id)
            Comentario.objects.create(
                publicacion=post,
                usuario=request.user,
                contenido=texto
            )
    return redirect('feed')
# Create your views here.
