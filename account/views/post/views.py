from django.http import JsonResponse
from django.contrib.auth.decorators import login_required 
from django.utils.timezone import now
from django.contrib import messages
from account.models import Post, Event, ImagePost, Volunteer
from datetime import datetime
from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
from datetime import date
import json

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
def load_posts(request, page):
    try:
        posts = Post.objects.prefetch_related("images").select_related("event", "user").order_by("-created_at")
        paginator = Paginator(posts, 20)
        page_obj = paginator.get_page(page)
        
        # Annotate posts with whether the user is a volunteer for their event
        for post in page_obj:
            if post.event:
                post.is_volunteer = Volunteer.objects.filter(event=post.event, user=request.user).exists()
            else:
                post.is_volunteer = False
                
        # Renderiza os posts como HTML usando o template parcial
        html = render_to_string("partials/post_list.html", {"page_obj": page_obj}, request=request)

        return JsonResponse({"html": html}, status=200)
    except Exception as e:
            print(e)
            return JsonResponse({
                "success": False,
                "message": "Erro ao buscar post!"
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

    return render(request, "apps/social/event.html", {
        "user_events": user_events,
        "other_events": other_events,
    })