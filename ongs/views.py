from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from account.models import Category
from django.db.models import Count, F
from django.utils.timezone import now
from account.models import Post, User

# página principal famosa feed page

@login_required
def index(request):
    user = request.user  # Usuário autenticado

    # Categorias disponíveis
    categories = Category.objects.all()

    # Lista de organizações que o usuário segue
    followed_organizations = user.following.filter(typeuser="organization")

    # Dois voluntários que o usuário ainda não segue
    non_followed_volunteers = User.objects.filter(
    typeuser="volunteer"
    ).exclude(
        id__in=user.following.values_list('id', flat=True)
    ).order_by("?")[:2]
    
    # Posts em alta (rankeados)
    # Fator de ranqueamento: likes, comentários e penalização por tempo
    posts_in_trend = (
        Post.objects.annotate(
            total_interactions=Count('likes') + Count('comments'),
            days_passed=now() - F('created_at')
        )
        .order_by('-total_interactions', 'days_passed')[:2]
    )

    return render(request, 'apps/social/feed.html', {
        'user': user,
        'categories': categories,
        'followed_organizations': followed_organizations,
        'non_followed_volunteers': non_followed_volunteers,
        'posts_in_trend': posts_in_trend,
    })

def termo_uso(request):
    return render(request, 'pages/termo_uso.html')