from django.http import JsonResponse
from django.contrib.auth.decorators import login_required 
from django.utils.timezone import now
from django.contrib import messages
from account.models import Post, Event, ImagePost, Volunteer, User, Comment
from datetime import datetime
from django.core.paginator import Paginator , EmptyPage
from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404 , redirect
from datetime import date
from django.db.models import Prefetch
import json
import re

@login_required
def create_post(request):
    if request.method == "POST":
        try:
            # Verifica se o usuário autenticado
            user = request.user
            data = request.POST.dict()  # Obtém os dados do POST
            images = request.FILES.getlist("images")  # Obtém os arquivos de imagem enviados
            
            # Verificação básica
            text = data.get("text", "").strip()
            event_data = json.loads(data.get("event", "{}"))  # Dados do evento, se enviados
            has_event = bool(event_data.get("title"))  # Determina se um evento será criado

            if not (text or images or has_event):
                return JsonResponse({
                    "success": False,
                    "message": "O post deve conter pelo menos texto, uma imagem ou um evento."
                }, status=400)

            # Cria o evento, se necessário
            event = None
            if has_event:
                datetime_str = event_data.get("datetime")  # Exemplo: "2024-11-29 16:01"
                if datetime_str:
                    try:
                        event_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
                        event_date = event_datetime.date()
                        event_time = event_datetime.time()
                    except ValueError:
                        return JsonResponse({
                            "success": False,
                            "message": "Formato inválido para data/hora do evento."
                        }, status=400)
                    
                    event = Event.objects.create(
                        user=user,
                        title=event_data.get("title", "").strip(),
                        description=event_data.get("description", "").strip(),
                        date=event_date,
                        time=event_time,
                    )

            # Cria o post
            post = Post.objects.create(
                user=user,
                text=text,
                event=event
            )
            
            # Salva as imagens associadas ao post
            for image in images:
                ImagePost.objects.create(
                    post=post,
                    image=image,
                    user=user
                )
            messages.success(request, "Post criado com Sucesso!")
            return JsonResponse({"success": True, "message": "Post criado com sucesso!"}, status=201)
        except Exception as e:
            print(e)
            return JsonResponse({
                "success": False,
                "message": "Erro ao criar o post. Tente novamente."
            }, status=500)
    return JsonResponse({"success": False, "message": "Método inválido."}, status=405)

@login_required
def load_posts(request, page=None, postId=None):
    try:
        # Define um Prefetch para buscar apenas 2 comentários mais recentes para cada post
        comments_prefetch = Prefetch(
            'comments',
            queryset=Comment.objects.order_by('-created_at')[:2],
            to_attr='recent_comments'
        )

        if postId:
            # Busca apenas o post com o ID informado
            posts = [get_object_or_404(Post.objects.prefetch_related(
                "images", comments_prefetch).select_related("event", "user"), id=postId)]
        else:
            # Busca os posts normalmente, ordenados por data de criação
            posts = Post.objects.prefetch_related("images", comments_prefetch).select_related(
                "event", "user").order_by("-created_at")

            # Paginador apenas se postId não for informado
            paginator = Paginator(posts, 20)  # Define 20 posts por página
            try:
                # Obtém os posts da página solicitada
                page_obj = paginator.page(page)
                posts = page_obj.object_list
            except EmptyPage:
                # Retorna uma resposta clara se a página não existir
                return JsonResponse({"html": "", "success": False}, status=200)

        # Adiciona informações adicionais (exemplo: voluntário)
        for post in posts:
            if post.event:
                post.is_volunteer = Volunteer.objects.filter(event=post.event, user=request.user).exists()
            else:
                post.is_volunteer = False

        # Renderiza os posts como HTML usando o template parcial
        html = render_to_string("partials/post_list.html", {"posts": posts}, request=request)
        print(posts, html)
        return JsonResponse({"html": html.strip(), "success": True}, status=200)

    except Exception as e:
        print(e)
        return JsonResponse({
            "success": False,
            "message": "Erro ao carregar posts!"
        }, status=500)
        
@login_required
def participar_evento(request, event_id):
    try:
        event = get_object_or_404(Event, id=event_id)

        # Verifica se o usuário já é voluntário
        if Volunteer.objects.filter(event=event, user=request.user).exists():
            return JsonResponse({"success": False, "message": "Você já está participando deste evento!"}, status=400)

        # Adiciona o usuário como voluntário
        Volunteer.objects.create(event=event, user=request.user)
        return JsonResponse({"success": True, "message": "Você agora está participando do evento!"}, status=200)
    except Exception as e:
            print(e)
            return JsonResponse({
                "success": False,
                "message": "Erro ao buscar post!"
            }, status=500)
            
@login_required
def event_list(request):
    
    # Filtra eventos futuros
    today = date.today()
    user_events = Event.objects.filter(user=request.user, date__gte=today).order_by("date")
    other_events = Event.objects.exclude(user=request.user).filter(date__gte=today).order_by("date")
    
    for event in other_events:
        event.is_volunteer = Volunteer.objects.filter(event=event, user=request.user).exists()
           
    return render(request, "apps/social/event.html", {
        "user_events": user_events,
        "other_events": other_events,
    })
    
    
@login_required
def delete_event(request, event_id):
    try:
        if request.method == "POST":
            event = get_object_or_404(Event, id=event_id)
                
            # Verifica se o usuário tem permissão para deletar
            if event.user != request.user:
                messages.error(request, "Você não tem permissão para excluir este evento.")
                return redirect('events')
            
            # Verifica se o evento está associado a um post vazio
            posts = event.posts.all()  # Relacionamento de posts com o evento
            for post in posts:
                if not post.text.strip() and not post.images.exists():  # Verifica se o texto está vazio e não há imagens
                    post.delete()  # Exclui o post vazio

            # Exclui o evento
            event.delete()
            messages.success(request, "Evento excluído com sucesso.")
            return redirect('events')
        else:
            messages.error(request, "Método não permitido.")

    except Exception as e:
        print(e)
        messages.error(request, "Erro ao Excluir evento!")
        
    return redirect('events')
    

def add_comment(request, post_id):
    if request.method == "POST":
        content = request.POST.get("content", "").strip()
        mentioned_user_id = request.POST.get("mentioned_user")
        print(request.POST)
        post = get_object_or_404(Post, id=post_id)

        # Processa o usuário mencionado
        mentioned_user = None
        if mentioned_user_id:
            mentioned_user = User.objects.filter(id=mentioned_user_id).first()
            if mentioned_user:
                content = f"@{mentioned_user.username} {content}"

        # Cria o comentário
        comment = Comment.objects.create(
            post=post,
            user=request.user,
            content=content,
        )

        # Adiciona o usuário mencionado ao campo ManyToMany, se aplicável
        if mentioned_user:
            comment.mentioned_users.add(mentioned_user)

        # Renderizar o novo comentário como HTML
        comment_html = render_to_string(
            "partials/comment.html", {"comment": comment}, request=request
        )

        return JsonResponse({"success": True, "comment_html": comment_html})

    return JsonResponse({"success": False, "message": "Método inválido."})

@login_required
def load_comments(request, post_id, page):
    try:
        post = get_object_or_404(Post, id=post_id)
        comments = post.comments.order_by('-created_at')
        paginator = Paginator(comments, 2)  # Define 2 comentários por página
        page_obj = paginator.get_page(page)

        html = ""
        for comment in page_obj:
            html += render_to_string("partials/comment.html", {"comment": comment}, request=request)

        return JsonResponse({
            "success": True,
            "html": html,
            "has_next": page_obj.has_next(),
        })

    except Exception as e:
        print(e)
        return JsonResponse({"success": False, "message": "Erro ao carregar comentários!"}, status=500)
    
@login_required
def add_like(request, post_id):
    if request.method == "POST":
        try:
            post = get_object_or_404(Post, id=post_id)
            user = request.user

            if post.likes.filter(id=user.id).exists():
                # Se o usuário já curtiu, remove a curtida
                post.likes.remove(user)
                liked = False
            else:
                # Caso contrário, adiciona a curtida
                post.likes.add(user)
                liked = True

            return JsonResponse({
                "liked": liked,
                "like_count": post.likes.count(),
            })

        except Exception as e:
            print(e)
            return JsonResponse({"error": "Erro ao processar a curtida."}, status=500)
    else:
        return JsonResponse({"error": "Método não permitido."}, status=405)